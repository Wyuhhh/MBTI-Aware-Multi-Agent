"""
双Judge评估系统 + Krippendorff α 一致性计算

Judge1 (异质): Oracle (INTJ+ENFP+ISTJ)
Judge2 (同质): Homogeneous (3x INTJ)

评估指标：
1. 双Judge评分对比
2. Krippendorff α 一致性
3. 统计显著性检验
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime

import numpy as np

from src.llm.client import LLMClient, MockLLMClient
from src.agent.base import MBTIAgent
from src.agent.debate import DebateManager
from benchmark.baselines.core import (
    HomogeneousBaseline,
    OracleBaseline,
    BaselineResult,
)


class ResponseQuality(Enum):
    """回答质量等级"""
    EXCELLENT = 4
    GOOD = 3
    AVERAGE = 2
    BELOW_AVERAGE = 1
    POOR = 0


@dataclass
class JudgeResponse:
    """单个Judge的回应"""
    judge_id: str
    judge_type: str  # "heterogeneous" or "homogeneous"
    response: str
    confidence: float
    category: str
    question_id: str


@dataclass
class EvaluationPair:
    """一对评估结果"""
    question_id: str
    category: str
    question: str
    heterogeneous_response: JudgeResponse
    homogeneous_response: JudgeResponse
    quality_heterogeneous: ResponseQuality
    quality_homogeneous: ResponseQuality
    winner: str  # "heterogeneous", "homogeneous", "tie"
    winner_confidence: float


@dataclass
class KrippendorffResult:
    """Krippendorff α 计算结果"""
    alpha: float
    agreement: float
    n_observations: int
    n_raters: int
    interpretation: str


@dataclass
class EvaluationReport:
    """完整评估报告"""
    timestamp: str
    total_questions: int
    heterogeneous_wins: int
    homogeneous_wins: int
    ties: int
    heterogeneous_win_rate: float
    avg_quality_heterogeneous: float
    avg_quality_homogeneous: float
    quality_improvement: float
    krippendorff_alpha: KrippendorffResult
    category_breakdown: Dict[str, Dict[str, Any]]
    statistical_significance: Dict[str, Any]
    evaluation_pairs: List[EvaluationPair]


class QualityJudge:
    """质量Judge - 评估回答质量"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.debate_manager = DebateManager(max_rounds=1)

    def judge_response(self, response: str, category: str) -> Tuple[ResponseQuality, float]:
        """
        Judge一个回答的质量

        Returns:
            (quality, confidence)
        """
        prompt = f"""你是一个专业的回答质量评估专家。请评估以下回答的质量。

回答类别: {category}

评估标准（0-4分）:
- 4分(优秀): 回答全面、深入、有独特见解，逻辑清晰
- 3分(良好): 回答合理、有一定深度，逻辑清楚
- 2分(一般): 回答基本合理，但缺乏深度
- 1分(较差): 回答有明显疏漏或逻辑问题
- 0分(差): 回答不相关或严重错误

回答内容:
---
{response[:1000]}
---

请只输出一个数字（0-4）和一个置信度（0-1），格式如下：
分数: X
置信度: Y

例如：
分数: 3
置信度: 0.85
"""

        try:
            result = self.llm_client.generate(prompt, temperature=0.3)
            lines = result.strip().split('\n')
            score = 2  # 默认
            confidence = 0.5

            for line in lines:
                if '分数' in line or 'score' in line.lower():
                    try:
                        score = int(line.split(':')[-1].strip())
                    except:
                        pass
                if '置信度' in line or 'confidence' in line.lower():
                    try:
                        confidence = float(line.split(':')[-1].strip())
                    except:
                        pass

            quality = ResponseQuality(max(0, min(4, score)))
            return quality, confidence
        except Exception as e:
            return ResponseQuality.AVERAGE, 0.5


class ComparativeJudge:
    """比较Judge - 判断两个回答哪个更好"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def compare(
        self,
        response_a: str,
        response_b: str,
        category: str,
        label_a: str = "A",
        label_b: str = "B",
    ) -> Tuple[str, float]:
        """
        比较两个回答

        Returns:
            (winner: "A"/"B"/"tie", confidence)
        """
        prompt = f"""你是一个专业的回答比较专家。请判断两个回答的质量高低。

问题类别: {category}

回答A:
---
{response_a[:800]}
---

回答B:
---
{response_b[:800]}
---

请判断哪个回答更好（A、B或平局）。

评估标准：
- 谁更能解决实际问题
- 谁的逻辑更清晰
- 谁提供更有价值的见解
- 谁的回答更全面

请只输出以下格式之一：
A更好|置信度:X
B更好|置信度:X
平局|置信度:X

例如：A更好|置信度:0.75
"""

        try:
            result = self.llm_client.generate(prompt, temperature=0.3)

            if 'A更好' in result or ('A' in result and 'B' not in result and '平局' not in result):
                winner = label_a
                conf = 0.5
                if '置信度' in result:
                    try:
                        conf = float(result.split('置信度:')[-1].strip())
                    except:
                        pass
                return winner, conf
            elif 'B更好' in result:
                return label_b, 0.5
            elif '平局' in result:
                return "tie", 0.5
            else:
                # 默认平局
                return "tie", 0.5
        except Exception as e:
            return "tie", 0.5


class KrippendorffAlpha:
    """Krippendorff α 一致性计算"""

    @staticmethod
    def calculate(
        ratings: List[List[float]],
        missing_values: Optional[List] = None,
    ) -> KrippendorffResult:
        """
        计算Krippendorff's Alpha

        Args:
            ratings: n x m 矩阵，n个观察值，m个评分者
            missing_values: 缺失值标记列表

        Returns:
            KrippendorffResult
        """
        ratings = np.array(ratings)
        n_observations, n_raters = ratings.shape

        if missing_values is None:
            missing_values = [np.nan]

        # 将缺失值设为NaN
        for mv in missing_values:
            ratings = np.where(ratings == mv, np.nan, ratings)

        # 计算实际配对数
        valid_pairs = 0
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                valid_pairs += np.sum(~np.isnan(ratings[:, i]) & ~np.isnan(ratings[:, j]))

        if valid_pairs == 0:
            return KrippendorffResult(
                alpha=1.0,
                agreement=1.0,
                n_observations=n_observations,
                n_raters=n_raters,
                interpretation="无有效配对数据",
            )

        # 计算 observed coincidence
        Do = 0
        for i in range(n_raters):
            for j in range(i + 1, n_raters):
                mask = ~np.isnan(ratings[:, i]) & ~np.isnan(ratings[:, j])
                if np.sum(mask) > 0:
                    diff = ratings[mask, i] - ratings[mask, j]
                    Do += np.sum(diff ** 2)

        # 计算 expected coincidence (假设随机)
        all_values = ratings[~np.isnan(ratings)]
        value_counts = {}
        for v in all_values:
            v_rounded = round(v, 2)
            value_counts[v_rounded] = value_counts.get(v_rounded, 0) + 1

        total_count = len(all_values)
        if total_count == 0:
            return KrippendorffResult(
                alpha=1.0,
                agreement=1.0,
                n_observations=n_observations,
                n_raters=n_raters,
                interpretation="无有效数据",
            )

        De = 0
        for v1, c1 in value_counts.items():
            for v2, c2 in value_counts.items():
                if v1 <= v2:  # 避免重复
                    coincidence = c1 * c2 if v1 != v2 else c1 * (c1 - 1)
                    De += coincidence * ((v1 - v2) ** 2)

        if De == 0:
            alpha = 1.0
        else:
            alpha = 1.0 - (Do / De)

        # 计算协议率
        agreement = 1.0 - (Do / (2 * total_count)) if total_count > 0 else 0

        # 解释
        if alpha >= 0.8:
            interpretation = "一致性优秀 (α ≥ 0.8)"
        elif alpha >= 0.667:
            interpretation = "一致性可接受 (0.667 ≤ α < 0.8)"
        elif alpha >= 0.5:
            interpretation = "一致性一般 (0.5 ≤ α < 0.667)"
        else:
            interpretation = "一致性差 (α < 0.5)，需改进"

        return KrippendorffResult(
            alpha=alpha,
            agreement=agreement,
            n_observations=n_observations,
            n_raters=n_raters,
            interpretation=interpretation,
        )


class DualJudgeEvaluator:
    """双Judge评估器"""

    def __init__(
        self,
        llm_client: LLMClient,
        quality_judge: Optional[QualityJudge] = None,
        comparative_judge: Optional[ComparativeJudge] = None,
    ):
        self.llm_client = llm_client
        self.quality_judge = quality_judge or QualityJudge(llm_client)
        self.comparative_judge = comparative_judge or ComparativeJudge(llm_client)
        self.debate_manager = DebateManager(max_rounds=2)

    def run_evaluation(
        self,
        questions: List[Dict],
        verbose: bool = True,
    ) -> EvaluationReport:
        """运行双Judge评估"""
        evaluation_pairs = []
        heterogeneous_wins = 0
        homogeneous_wins = 0
        ties = 0

        total = len(questions)
        for idx, q in enumerate(questions):
            if verbose:
                print(f"  [{idx+1}/{total}] {q['id']}: {q['question'][:50]}...")

            # Judge1: 异质Agent (Oracle)
            het_baseline = OracleBaseline(self.llm_client, debate_rounds=2)
            het_result = het_baseline.run(q["question"])
            heterogeneous_response = JudgeResponse(
                judge_id="heterogeneous",
                judge_type="heterogeneous",
                response=het_result.final_consensus,
                confidence=het_result.confidence,
                category=q["category"],
                question_id=q["id"],
            )

            # Judge2: 同质Agent (Homogeneous INTJ)
            hom_baseline = HomogeneousBaseline(self.llm_client, mbti_type="INTJ", debate_rounds=2)
            hom_result = hom_baseline.run(q["question"])
            homogeneous_response = JudgeResponse(
                judge_id="homogeneous",
                judge_type="homogeneous",
                response=hom_result.final_consensus,
                confidence=hom_result.confidence,
                category=q["category"],
                question_id=q["id"],
            )

            # 评估质量
            quality_het, _ = self.quality_judge.judge_response(
                heterogeneous_response.response, q["category"]
            )
            quality_hom, _ = self.quality_judge.judge_response(
                homogeneous_response.response, q["category"]
            )

            # 比较判断
            winner, win_conf = self.comparative_judge.compare(
                heterogeneous_response.response,
                homogeneous_response.response,
                q["category"],
                label_a="heterogeneous",
                label_b="homogeneous",
            )

            pair = EvaluationPair(
                question_id=q["id"],
                category=q["category"],
                question=q["question"],
                heterogeneous_response=heterogeneous_response,
                homogeneous_response=homogeneous_response,
                quality_heterogeneous=quality_het,
                quality_homogeneous=quality_hom,
                winner=winner,
                winner_confidence=win_conf,
            )
            evaluation_pairs.append(pair)

            if winner == "heterogeneous":
                heterogeneous_wins += 1
            elif winner == "homogeneous":
                homogeneous_wins += 1
            else:
                ties += 1

        # 计算Krippendorff α
        # 使用质量分数作为评分数据
        ratings = []
        for pair in evaluation_pairs:
            ratings.append([
                pair.quality_heterogeneous.value,
                pair.quality_homogeneous.value,
            ])

        krippendorff_result = KrippendorffAlpha.calculate(ratings)

        # 类别分析
        category_breakdown = self._analyze_by_category(evaluation_pairs)

        # 统计显著性 (McNemar检验)
        stat_sig = self._statistical_significance(
            heterogeneous_wins, homogeneous_wins, ties, total
        )

        # 计算平均质量
        avg_quality_het = np.mean([p.quality_heterogeneous.value for p in evaluation_pairs])
        avg_quality_hom = np.mean([p.quality_homogeneous.value for p in evaluation_pairs])

        report = EvaluationReport(
            timestamp=datetime.now().isoformat(),
            total_questions=total,
            heterogeneous_wins=heterogeneous_wins,
            homogeneous_wins=homogeneous_wins,
            ties=ties,
            heterogeneous_win_rate=heterogeneous_wins / total if total > 0 else 0,
            avg_quality_heterogeneous=avg_quality_het,
            avg_quality_homogeneous=avg_quality_hom,
            quality_improvement=avg_quality_het - avg_quality_hom,
            krippendorff_alpha=krippendorff_result,
            category_breakdown=category_breakdown,
            statistical_significance=stat_sig,
            evaluation_pairs=evaluation_pairs,
        )

        return report

    def _analyze_by_category(
        self, pairs: List[EvaluationPair]
    ) -> Dict[str, Dict[str, Any]]:
        """按类别分析"""
        categories = {}
        for pair in pairs:
            cat = pair.category
            if cat not in categories:
                categories[cat] = {
                    "total": 0,
                    "het_wins": 0,
                    "hom_wins": 0,
                    "ties": 0,
                    "avg_quality_het": [],
                    "avg_quality_hom": [],
                }

            categories[cat]["total"] += 1
            categories[cat]["avg_quality_het"].append(pair.quality_heterogeneous.value)
            categories[cat]["avg_quality_hom"].append(pair.quality_homogeneous.value)

            if pair.winner == "heterogeneous":
                categories[cat]["het_wins"] += 1
            elif pair.winner == "homogeneous":
                categories[cat]["hom_wins"] += 1
            else:
                categories[cat]["ties"] += 1

        # 计算汇总统计
        for cat, data in categories.items():
            data["het_win_rate"] = data["het_wins"] / data["total"] if data["total"] > 0 else 0
            data["avg_quality_het"] = np.mean(data["avg_quality_het"]) if data["avg_quality_het"] else 0
            data["avg_quality_hom"] = np.mean(data["avg_quality_hom"]) if data["avg_quality_hom"] else 0

        return categories

    def _statistical_significance(
        self,
        het_wins: int,
        hom_wins: int,
        ties: int,
        total: int,
    ) -> Dict[str, Any]:
        """
        McNemar检验判断统计显著性

        零假设：异质Agent和同质Agent的胜率相等
        """
        # 简化的二项检验
        # 在ties情况下，随机分配胜负
        effective_n = het_wins + hom_wins
        if effective_n == 0:
            return {
                "test": "McNemar",
                "p_value": 1.0,
                "significant": False,
                "interpretation": "无有效对比数据",
            }

        # 期望异质胜率（如果零假设为真）
        expected_rate = 0.5

        # 观察到的异质胜率
        observed_rate = het_wins / effective_n if effective_n > 0 else 0

        # 简化的z检验
        from scipy import stats
        n = effective_n
        p = 0.5
        se = np.sqrt(p * (1 - p) / n) if n > 0 else 0

        if se > 0:
            z = (observed_rate - p) / se
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))  # 双尾检验
        else:
            z = 0
            p_value = 1.0

        return {
            "test": "McNemar (simplified z-test)",
            "z_score": z,
            "p_value": p_value,
            "significant": p_value < 0.05,
            "interpretation": (
                "差异显著 (p < 0.05)" if p_value < 0.05
                else "差异不显著 (p ≥ 0.05)"
            ),
        }


def run_dual_judge_evaluation(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    questions: Optional[List[Dict]] = None,
    categories: Optional[List[str]] = None,
    verbose: bool = True,
) -> EvaluationReport:
    """运行双Judge评估的便捷函数"""

    # 创建LLM客户端
    if provider == "mock":
        llm_client = MockLLMClient()
    else:
        from src.llm.client import OpenAIClient
        llm_client = OpenAIClient(api_key=api_key, model=model)

    # 加载问题集
    if questions is None:
        from benchmark.datasets.evaluation_200 import get_dataset
        all_questions = get_dataset()
        if categories:
            questions = [q for q in all_questions if q["category"] in categories]
        else:
            questions = all_questions

    print(f"\n{'#'*60}")
    print(f"# 双Judge评估 (Heterogeneous vs Homogeneous)")
    print(f"# Total questions: {len(questions)}")
    print(f"# Provider: {provider}")
    print(f"{'#'*60}\n")

    evaluator = DualJudgeEvaluator(llm_client)
    report = evaluator.run_evaluation(questions, verbose=verbose)

    # 打印汇总
    print(f"\n{'='*60}")
    print("双Judge评估汇总")
    print(f"{'='*60}")
    print(f"\n异质Agent (Oracle) 胜率: {report.heterogeneous_win_rate:.1%}")
    print(f"同质Agent (Homogeneous) 胜率: {report.homogeneous_wins / report.total_questions:.1%}")
    print(f"平局率: {report.ties / report.total_questions:.1%}")

    print(f"\n平均质量分:")
    print(f"  异质Agent: {report.avg_quality_heterogeneous:.2f}")
    print(f"  同质Agent: {report.avg_quality_homogeneous:.2f}")
    print(f"  质量提升: +{report.quality_improvement:.2f}")

    print(f"\nKrippendorff's Alpha: {report.krippendorff_alpha.alpha:.3f}")
    print(f"  解释: {report.krippendorff_alpha.interpretation}")

    print(f"\n统计显著性:")
    print(f"  p-value: {report.statistical_significance['p_value']:.4f}")
    print(f"  {report.statistical_significance['interpretation']}")

    print(f"\n{'='*60}")
    print("类别细分")
    print(f"{'='*60}")
    for cat, data in report.category_breakdown.items():
        print(f"\n{cat}:")
        print(f"  异质胜率: {data['het_win_rate']:.1%}")
        print(f"  平均质量: 异质={data['avg_quality_het']:.2f}, 同质={data['avg_quality_hom']:.2f}")

    return report


if __name__ == "__main__":
    import argparse
    from benchmark.datasets.evaluation_200 import get_dataset

    parser = argparse.ArgumentParser(description="双Judge评估")
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default="gpt-4")
    parser.add_argument("--categories", nargs="*", default=None)
    parser.add_argument("--limit", type=int, default=None, help="限制问题数量（用于快速测试）")

    args = parser.parse_args()

    questions = get_dataset()
    if args.categories:
        questions = [q for q in questions if q["category"] in args.categories]
    if args.limit:
        questions = questions[:args.limit]

    report = run_dual_judge_evaluation(
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
        questions=questions,
        verbose=True,
    )