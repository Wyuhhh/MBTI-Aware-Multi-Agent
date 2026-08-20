"""
评测主脚本

运行200题评测，对比4组基线
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.client import LLMClient, MockLLMClient, OpenAIClient
from src.main import MBTIMultiAgentSystem
from benchmark.baselines.core import (
    BaselineRunner,
    HomogeneousBaseline,
    RandomMBTIBaseline,
    SingleBestBaseline,
    OracleBaseline,
    BaselineResult,
)
from benchmark.datasets.evaluation_200 import get_dataset, get_categories, get_category_stats


@dataclass
class QuestionResult:
    """单题评测结果"""
    question_id: str
    category: str
    question: str
    baseline_results: Dict[str, BaselineResult]
    timestamp: str


@dataclass
class CategoryResult:
    """类别汇总结果"""
    category: str
    num_questions: int
    baseline_scores: Dict[str, float]  # baseline_name -> avg_score
    baseline_confidences: Dict[str, float]


@dataclass
class BenchmarkReport:
    """完整评测报告"""
    timestamp: str
    total_questions: int
    categories: List[str]
    question_results: List[QuestionResult]
    category_summaries: List[CategoryResult]
    overall_comparison: Dict[str, Any]


class BenchmarkEvaluator:
    """评测器"""

    def __init__(
        self,
        llm_client: LLMClient,
        debate_rounds: int = 2,
        output_dir: str = "benchmark/results",
    ):
        self.llm_client = llm_client
        self.debate_rounds = debate_rounds
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_runner = BaselineRunner(llm_client)

    def evaluate_question(self, question: Dict) -> QuestionResult:
        """评测单题"""
        print(f"    Evaluating: {question['id']} - {question['question'][:50]}...")

        baseline_results = {}

        # 1. Homogeneous Baseline (INTJ)
        baseline = HomogeneousBaseline(
            self.llm_client,
            mbti_type="INTJ",
            debate_rounds=self.debate_rounds,
        )
        baseline_results["homogeneous_INTJ"] = baseline.run(question["question"])

        # 2. Random MBTI Baseline
        baseline = RandomMBTIBaseline(
            self.llm_client,
            debate_rounds=self.debate_rounds,
            seed=42,
        )
        baseline_results["random_mbti"] = baseline.run(question["question"])

        # 3. Single Best Baseline (INTJ)
        baseline = SingleBestBaseline(
            self.llm_client,
            mbti_type="INTJ",
        )
        baseline_results["single_INTJ"] = baseline.run(question["question"])

        # 4. Oracle Baseline (INTJ+ENFP+ISTJ)
        baseline = OracleBaseline(
            self.llm_client,
            debate_rounds=self.debate_rounds,
        )
        baseline_results["oracle"] = baseline.run(question["question"])

        return QuestionResult(
            question_id=question["id"],
            category=question["category"],
            question=question["question"],
            baseline_results=baseline_results,
            timestamp=datetime.now().isoformat(),
        )

    def evaluate_category(
        self,
        category: str,
        questions: List[Dict],
        verbose: bool = True,
    ) -> tuple[List[QuestionResult], CategoryResult]:
        """评测整个类别"""
        if verbose:
            print(f"\n{'='*60}")
            print(f"Category: {category} ({len(questions)} questions)")
            print(f"{'='*60}")

        question_results = []
        for q in questions:
            if verbose:
                print(f"  Question: {q['question'][:60]}...")
            result = self.evaluate_question(q)
            question_results.append(result)

        # 汇总类别结果
        baseline_scores = {}
        baseline_confs = {}
        for baseline_name in ["homogeneous_INTJ", "random_mbti", "single_INTJ", "oracle"]:
            scores = [r.baseline_results[baseline_name].confidence for r in question_results]
            baseline_scores[baseline_name] = sum(scores) / len(scores) if scores else 0
            baseline_confs[baseline_name] = sum(
                r.baseline_results[baseline_name].confidence for r in question_results
            ) / len(question_results) if question_results else 0

        category_result = CategoryResult(
            category=category,
            num_questions=len(questions),
            baseline_scores=baseline_scores,
            baseline_confidences=baseline_confs,
        )

        return question_results, category_result

    def run_full_benchmark(
        self,
        dataset: Optional[List[Dict]] = None,
        categories: Optional[List[str]] = None,
        verbose: bool = True,
    ) -> BenchmarkReport:
        """运行完整评测"""
        if dataset is None:
            dataset = get_dataset()

        if categories is None:
            categories = get_categories()

        print(f"\n{'#'*60}")
        print(f"# MBTI Multi-Agent Benchmark")
        print(f"# Total questions: {len(dataset)}")
        print(f"# Categories: {', '.join(categories)}")
        print(f"# Debate rounds: {self.debate_rounds}")
        print(f"{'#'*60}\n")

        all_question_results = []
        category_summaries = []
        start_time = time.time()

        for category in categories:
            cat_questions = [q for q in dataset if q["category"] == category]
            q_results, cat_result = self.evaluate_category(
                category, cat_questions, verbose=verbose
            )
            all_question_results.extend(q_results)
            category_summaries.append(cat_result)

            if verbose:
                print(f"\n  {category} Summary:")
                for name, score in cat_result.baseline_scores.items():
                    print(f"    {name}: {score:.3f}")

        elapsed = time.time() - start_time

        # Overall comparison
        overall_comparison = {
            "total_time_seconds": elapsed,
            "questions_per_second": len(dataset) / elapsed if elapsed > 0 else 0,
            "baseline_avg_scores": {},
        }

        for baseline_name in ["homogeneous_INTJ", "random_mbti", "single_INTJ", "oracle"]:
            scores = [cs.baseline_scores[baseline_name] for cs in category_summaries]
            overall_comparison["baseline_avg_scores"][baseline_name] = sum(scores) / len(scores)

        report = BenchmarkReport(
            timestamp=datetime.now().isoformat(),
            total_questions=len(dataset),
            categories=categories,
            question_results=all_question_results,
            category_summaries=category_summaries,
            overall_comparison=overall_comparison,
        )

        return report

    def save_report(self, report: BenchmarkReport, filename: Optional[str] = None):
        """保存报告"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"benchmark_report_{timestamp}.json"

        filepath = self.output_dir / filename

        # Convert dataclasses to dict for JSON serialization
        report_dict = {
            "timestamp": report.timestamp,
            "total_questions": report.total_questions,
            "categories": report.categories,
            "category_summaries": [asdict(cs) for cs in report.category_summaries],
            "overall_comparison": report.overall_comparison,
            "question_results": [
                {
                    "question_id": qr.question_id,
                    "category": qr.category,
                    "question": qr.question,
                    "timestamp": qr.timestamp,
                    "baseline_results": {
                        name: {
                            "name": br.name,
                            "agents_used": br.agents_used,
                            "debate_rounds": br.debate_rounds,
                            "final_consensus": br.final_consensus,
                            "confidence": br.confidence,
                            "metadata": br.metadata,
                        }
                        for name, br in qr.baseline_results.items()
                    },
                }
                for qr in report.question_results
            ],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)

        print(f"\nReport saved to: {filepath}")
        return filepath

    def print_summary(self, report: BenchmarkReport):
        """打印汇总"""
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}")
        print(f"\nTotal questions: {report.total_questions}")
        print(f"Categories: {', '.join(report.categories)}")
        print(f"Total time: {report.overall_comparison['total_time_seconds']:.1f}s")
        print(f"Speed: {report.overall_comparison['questions_per_second']:.1f} q/s")

        print(f"\n{'='*60}")
        print("OVERALL BASELINE COMPARISON")
        print(f"{'='*60}")
        print(f"\n{'Baseline':<25} {'Avg Confidence':<15}")
        print("-" * 40)
        for name, score in report.overall_comparison["baseline_avg_scores"].items():
            print(f"{name:<25} {score:.3f}")

        print(f"\n{'='*60}")
        print("CATEGORY BREAKDOWN")
        print(f"{'='*60}")
        for cs in report.category_summaries:
            print(f"\n{cs.category} ({cs.num_questions} questions):")
            for name, score in cs.baseline_scores.items():
                print(f"  {name:<20} {score:.3f}")


def run_benchmark(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    debate_rounds: int = 2,
    categories: Optional[List[str]] = None,
    save_report: bool = True,
    verbose: bool = True,
):
    """运行评测的便捷函数"""
    # 创建LLM客户端
    if provider == "mock":
        llm_client = MockLLMClient()
    elif provider == "openai":
        llm_client = OpenAIClient(api_key=api_key, model=model)
    elif provider == "minimax":
        from src.llm.client import MiniMaxClient
        llm_client = MiniMaxClient(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    # 创建评测器
    evaluator = BenchmarkEvaluator(
        llm_client=llm_client,
        debate_rounds=debate_rounds,
    )

    # 运行评测
    report = evaluator.run_full_benchmark(
        categories=categories,
        verbose=verbose,
    )

    # 打印汇总
    evaluator.print_summary(report)

    # 保存报告
    if save_report:
        evaluator.save_report(report)

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MBTI Multi-Agent Benchmark")
    parser.add_argument("--provider", default="mock", choices=["mock", "openai"])
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default="gpt-4")
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--categories", nargs="*", default=None)
    parser.add_argument("--no-save", action="store_true")
    parser.add_argument("--quiet", action="store_true")

    args = parser.parse_args()

    run_benchmark(
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
        debate_rounds=args.rounds,
        categories=args.categories,
        save_report=not args.no_save,
        verbose=not args.quiet,
    )