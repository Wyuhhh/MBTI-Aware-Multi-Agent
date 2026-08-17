"""
统计分析模块 - 多次运行 + 置信区间 + 统计显著性

解决LLM随机性导致的可复现性问题
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import json
from datetime import datetime
import math

import numpy as np
from scipy import stats

from src.llm.client import LLMClient, MockLLMClient
from src.agent.base import MBTIAgent
from benchmark.baselines.core import HomogeneousBaseline, OracleBaseline, BaselineResult


@dataclass
class MultiRunResult:
    """多次运行结果"""
    metric_name: str
    n_runs: int
    mean: float
    std: float
    min: float
    max: float
    median: float
    ci_95: Tuple[float, float]
    ci_99: Tuple[float, float]

    def __str__(self):
        return (
            f"{self.metric_name}:\n"
            f"  n={self.n_runs}, mean={self.mean:.4f}, std={self.std:.4f}\n"
            f"  95% CI: [{self.ci_95[0]:.4f}, {self.ci_95[1]:.4f}]\n"
            f"  Range: [{self.min:.4f}, {self.max:.4f}]"
        )


@dataclass
class SignificanceTestResult:
    """显著性检验结果"""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    interpretation: str


@dataclass
class StatisticalReport:
    """完整统计分析报告"""
    timestamp: str
    n_runs: int
    questions_tested: int
    baseline_stats: Dict[str, Dict[str, MultiRunResult]]
    comparison_results: Dict[str, SignificanceTestResult]
    is_significant: bool
    summary: str


class StatisticalAnalyzer:
    """统计分析器"""

    def __init__(
        self,
        llm_client: LLMClient,
        n_runs: int = 5,
    ):
        self.llm_client = llm_client
        self.n_runs = n_runs

    def _calculate_ci(
        self,
        data: List[float],
        confidence: float = 0.95,
    ) -> Tuple[float, float]:
        """计算置信区间"""
        if len(data) < 2:
            return (data[0] if data else 0, data[0] if data else 0)

        mean = np.mean(data)
        se = stats.sem(data)  # 标准误差
        ci = stats.t.interval(confidence, len(data) - 1, loc=mean, scale=se)
        return ci

    def _calculate_stats(self, values: List[float], metric_name: str) -> MultiRunResult:
        """计算基本统计量"""
        if not values:
            return MultiRunResult(
                metric_name=metric_name,
                n_runs=0,
                mean=0, std=0, min=0, max=0, median=0,
                ci_95=(0, 0), ci_99=(0, 0),
            )

        return MultiRunResult(
            metric_name=metric_name,
            n_runs=len(values),
            mean=np.mean(values),
            std=np.std(values),
            min=np.min(values),
            max=np.max(values),
            median=np.median(values),
            ci_95=self._calculate_ci(values, 0.95),
            ci_99=self._calculate_ci(values, 0.99),
        )

    def _run_single_baseline(
        self,
        baseline_class,
        question: str,
    ) -> Dict[str, float]:
        """单次运行单个基线"""
        baseline = baseline_class(self.llm_client)
        result = baseline.run(question)

        return {
            "confidence": result.confidence,
            "response_length": len(result.final_consensus),
            "num_messages": result.metadata.get("num_messages", 0),
        }

    def run_multi_baseline_multi_question(
        self,
        baselines: Dict[str, Any],
        questions: List[Dict],
        n_runs: Optional[int] = None,
    ) -> Dict[str, Dict[str, List[float]]]:
        """
        多次运行多个基线在多个问题上

        Returns:
            {baseline_name: {metric_name: [values per run]}}
        """
        if n_runs is None:
            n_runs = self.n_runs

        all_metrics = defaultdict(lambda: defaultdict(list))

        for run_idx in range(n_runs):
            print(f"  Run {run_idx + 1}/{n_runs}...")

            for baseline_name, baseline_class in baselines.items():
                run_confidences = []
                run_lengths = []

                for q in questions:
                    try:
                        result = self._run_single_baseline(baseline_class, q["question"])
                        run_confidences.append(result["confidence"])
                        run_lengths.append(result["response_length"])
                    except Exception as e:
                        print(f"    Error on {baseline_name}/{q['id']}: {e}")

                if run_confidences:
                    all_metrics[baseline_name]["confidence"].append(np.mean(run_confidences))
                    all_metrics[baseline_name]["response_length"].append(np.mean(run_lengths))

        return dict(all_metrics)

    def compare_baselines(
        self,
        metrics_a: List[float],
        metrics_b: List[float],
        baseline_a_name: str = "Baseline A",
        baseline_b_name: str = "Baseline B",
    ) -> SignificanceTestResult:
        """
        比较两个基线的显著性差异

        使用配对t检验（适用于同一组问题的多次测量）
        """
        if len(metrics_a) != len(metrics_b) or len(metrics_a) < 2:
            return SignificanceTestResult(
                test_name="t-test",
                statistic=0,
                p_value=1.0,
                significant=False,
                interpretation="数据不足，无法进行显著性检验",
            )

        # 配对t检验
        t_stat, p_value = stats.ttest_rel(metrics_a, metrics_b)

        # 也计算Cohen's d效应量
        diff = np.mean(metrics_a) - np.mean(metrics_b)
        pooled_std = np.sqrt((np.var(metrics_a) + np.var(metrics_b)) / 2)
        cohens_d = diff / pooled_std if pooled_std > 0 else 0

        significant = p_value < 0.05

        # 解释
        if p_value < 0.01:
            interp = f"{baseline_a_name}显著优于{baseline_b_name} (p < 0.01)"
        elif p_value < 0.05:
            interp = f"{baseline_a_name}显著优于{baseline_b_name} (p < 0.05)"
        else:
            interp = f"两基线之间无显著差异 (p >= 0.05)"

        # 加入效应量
        if abs(cohens_d) < 0.2:
            interp += f", 效应量小 (d={cohens_d:.2f})"
        elif abs(cohens_d) < 0.5:
            interp += f", 效应量中等 (d={cohens_d:.2f})"
        else:
            interp += f", 效应量大 (d={cohens_d:.2f})"

        return SignificanceTestResult(
            test_name="Paired t-test",
            statistic=t_stat,
            p_value=p_value,
            significant=significant,
            interpretation=interp,
        )

    def run_full_analysis(
        self,
        baselines: Dict[str, Any],
        questions: List[Dict],
        n_runs: Optional[int] = None,
        verbose: bool = True,
    ) -> StatisticalReport:
        """运行完整统计分析"""
        if n_runs is None:
            n_runs = self.n_runs

        if verbose:
            print(f"\n{'='*60}")
            print(f"统计分析")
            print(f"基线: {list(baselines.keys())}")
            print(f"问题数: {len(questions)}")
            print(f"每基线运行次数: {n_runs}")
            print(f"{'='*60}\n")

        # 多次运行收集数据
        raw_metrics = self.run_multi_baseline_multi_question(
            baselines, questions, n_runs
        )

        # 计算各基线的统计量
        baseline_stats = {}
        for baseline_name, metrics in raw_metrics.items():
            baseline_stats[baseline_name] = {}
            for metric_name, values in metrics.items():
                baseline_stats[baseline_name][metric_name] = self._calculate_stats(
                    values, f"{baseline_name}_{metric_name}"
                )

        # 两两比较显著性
        comparison_results = {}
        baseline_names = list(baselines.keys())

        for i in range(len(baseline_names)):
            for j in range(i + 1, len(baseline_names)):
                name_a = baseline_names[i]
                name_b = baseline_names[j]

                # 比较置信度
                key_a = f"{name_a}_confidence"
                key_b = f"{name_b}_confidence"

                if (key_a in baseline_stats and key_b in baseline_stats and
                    baseline_stats[key_a] and baseline_stats[key_b]):

                    metrics_a = raw_metrics[name_a]["confidence"]
                    metrics_b = raw_metrics[name_b]["confidence"]

                    comparison_results[f"{name_a}_vs_{name_b}"] = self.compare_baselines(
                        metrics_a, metrics_b, name_a, name_b
                    )

        # 判断是否有显著差异
        any_significant = any(
            r.significant for r in comparison_results.values()
        )

        # 生成汇总
        summary_parts = []
        for name, result in comparison_results.items():
            if result.significant:
                summary_parts.append(result.interpretation)

        report = StatisticalReport(
            timestamp=datetime.now().isoformat(),
            n_runs=n_runs,
            questions_tested=len(questions),
            baseline_stats=baseline_stats,
            comparison_results=comparison_results,
            is_significant=any_significant,
            summary="; ".join(summary_parts) if summary_parts else "所有基线之间无显著差异",
        )

        return report


def run_statistical_analysis(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    baselines: Optional[Dict[str, Any]] = None,
    questions: Optional[List[Dict]] = None,
    n_runs: int = 3,
    verbose: bool = True,
) -> StatisticalReport:
    """运行统计分析的便捷函数"""

    if baselines is None:
        baselines = {
            "homogeneous_INTJ": HomogeneousBaseline,
            "oracle": OracleBaseline,
        }

    # 创建LLM客户端
    if provider == "mock":
        llm_client = MockLLMClient()
    else:
        from src.llm.client import OpenAIClient
        llm_client = OpenAIClient(api_key=api_key, model=model)

    # 加载问题
    if questions is None:
        from benchmark.datasets.evaluation_200 import get_dataset
        questions = get_dataset()[:15]

    # 运行分析
    analyzer = StatisticalAnalyzer(llm_client, n_runs=n_runs)
    report = analyzer.run_full_analysis(baselines, questions, verbose=verbose)

    # 打印报告
    if verbose:
        print(f"\n{'='*60}")
        print("统计分析结果")
        print(f"{'='*60}")

        print("\n各基线统计:")
        for baseline_name, metrics in report.baseline_stats.items():
            print(f"\n  {baseline_name}:")
            for metric_name, stat in metrics.items():
                print(f"    {stat}")

        print("\n显著性检验:")
        for name, result in report.comparison_results.items():
            sig_marker = "***" if result.p_value < 0.01 else ("**" if result.p_value < 0.05 else "")
            print(f"  {name} {sig_marker}")
            print(f"    {result.interpretation}")

        print(f"\n结论: {report.summary}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="统计分析")
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default="gpt-4")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--runs", type=int, default=3)

    args = parser.parse_args()

    from benchmark.datasets.evaluation_200 import get_dataset
    questions = get_dataset()[:args.limit]

    run_statistical_analysis(
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
        questions=questions,
        n_runs=args.runs,
        verbose=True,
    )