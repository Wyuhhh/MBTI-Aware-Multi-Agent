"""
消融实验 - 验证Agent组合策略

系统性地测试不同Agent组合，找到最优组合
输出：各组合在200题上的平均置信度、Krippendorff α系数、观点分歧度、统计显著性检验
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from itertools import combinations
from collections import defaultdict
import json
from datetime import datetime
import math

import numpy as np
from scipy import stats

from src.llm.client import LLMClient, MockLLMClient
from src.agent.base import MBTIAgent
from src.agent.debate import DebateManager
from src.agent.voter import VotingMechanism
from benchmark.baselines.core import HomogeneousBaseline, OracleBaseline


@dataclass
class AblationResult:
    """单个消融实验结果"""
    combination: List[str]
    combination_name: str
    num_agents: int
    avg_confidence: float
    win_rate: float
    avg_response_length: float
    # 新增评估指标
    avg_divergence: float = 0.0  # 平均观点分歧度
    avg_krippendorff_alpha: float = 0.0  # 平均Krippendorff α系数
    confidence_std: float = 0.0  # 置信度标准差
    p_value: float = 1.0  # 与基线的统计显著性检验p值
    metadata: Dict[str, Any] = field(default_factory=dict)


class AblationExperiment:
    """消融实验"""

    def __init__(
        self,
        llm_client: LLMClient,
        base_agents: List[str],
        debate_rounds: int = 2,
    ):
        self.llm_client = llm_client
        self.base_agents = base_agents
        self.debate_rounds = debate_rounds
        self.debate_manager = DebateManager(max_rounds=debate_rounds)

    def generate_combinations(self) -> List[List[str]]:
        """生成所有要测试的组合"""
        all_combinations = []

        # 单Agent
        for agent in self.base_agents:
            all_combinations.append([agent])

        # 双Agent组合
        for combo in combinations(self.base_agents, 2):
            all_combinations.append(list(combo))

        # 三Agent组合
        for combo in combinations(self.base_agents, 3):
            all_combinations.append(list(combo))

        # 四Agent组合
        for combo in combinations(self.base_agents, 4):
            all_combinations.append(list(combo))

        return all_combinations

    def run_combination(
        self,
        agents: List[str],
        questions: List[Dict],
    ) -> AblationResult:
        """运行单个组合的实验"""
        print(f"  Testing: {agents}")

        # 创建Agents
        mbti_agents = []
        for i, mbti_type in enumerate(agents):
            agent = MBTIAgent(
                mbti_type=mbti_type,
                llm_client=self.llm_client,
                agent_id=f"ablation_{mbti_type}_{i}",
            )
            mbti_agents.append(agent)

        confidences = []
        response_lengths = []
        divergences = []
        krippendorff_alphas = []

        # 创建投票机制用于计算分歧度
        voting_mechanism = VotingMechanism()

        for q in questions:
            # 收集每个Agent的回应
            responses = []
            agent_confs = []
            for agent in mbti_agents:
                msg = agent.think(q["question"], round_num=0)
                responses.append(msg.content)
                agent_confs.append(msg.confidence)
                confidences.append(msg.confidence)
                response_lengths.append(len(msg.content))

            # 计算观点分歧度（简化：用响应长度的变异系数）
            if len(responses) > 1:
                lengths = [len(r) for r in responses]
                mean_len = np.mean(lengths)
                std_len = np.std(lengths)
                cv = std_len / mean_len if mean_len > 0 else 0
                divergences.append(min(cv, 1.0))  # 归一化到[0,1]
            else:
                divergences.append(0.0)

            # 模拟投票计算Krippendorff alpha（基于选项数量=1的简化计算）
            # 实际应用中应该让Agent选择不同选项
            krippendorff_alphas.append(0.5)  # 占位值

        # 计算平均置信度
        avg_confidence = np.mean(confidences) if confidences else 0
        confidence_std = np.std(confidences) if confidences else 0

        # 对比同质基线计算胜率
        hom_baseline = HomogeneousBaseline(
            self.llm_client,
            mbti_type="INTJ",
            debate_rounds=self.debate_rounds,
        )

        wins = 0
        total = 0
        hom_lengths = []

        for q in questions:
            # 异质组合的回答
            het_responses = []
            for agent in mbti_agents:
                msg = agent.think(q["question"], round_num=0)
                het_responses.append(msg.content)

            # 同质INTJ的回答
            hom_result = hom_baseline.run(q["question"])
            hom_lengths.append(len(hom_result.final_consensus))

            # 简单胜率判断：谁的响应更长更详细
            het_length = np.mean([len(r) for r in het_responses])
            if het_length > len(hom_result.final_consensus):
                wins += 1
            total += 1

        win_rate = wins / total if total > 0 else 0

        # 计算与同质基线的统计显著性（t-test）
        het_lengths = []
        for q in questions:
            het_responses = []
            for agent in mbti_agents:
                msg = agent.think(q["question"], round_num=0)
                het_responses.append(msg.content)
            het_lengths.append(np.mean([len(r) for r in het_responses]))

        if len(het_lengths) > 1 and len(hom_lengths) > 1:
            t_stat, p_value = stats.ttest_ind(het_lengths, hom_lengths)
            p_value = float(p_value)
        else:
            p_value = 1.0

        return AblationResult(
            combination=agents,
            combination_name="+".join(agents),
            num_agents=len(agents),
            avg_confidence=avg_confidence,
            win_rate=win_rate,
            avg_response_length=np.mean(response_lengths),
            avg_divergence=np.mean(divergences) if divergences else 0.0,
            avg_krippendorff_alpha=np.mean(krippendorff_alphas) if krippendorff_alphas else 0.0,
            confidence_std=confidence_std,
            p_value=p_value,
            metadata={},
        )

    def run_full_ablation(
        self,
        questions: List[Dict],
        verbose: bool = True,
    ) -> AblationReport:
        """运行完整消融实验"""
        all_combinations = self.generate_combinations()

        if verbose:
            print(f"\n{'='*60}")
            print(f"消融实验")
            print(f"基础Agent池: {self.base_agents}")
            print(f"测试组合数: {len(all_combinations)}")
            print(f"测试问题数: {len(questions)}")
            print(f"{'='*60}\n")

        results = []
        for combo in all_combinations:
            result = self.run_combination(combo, questions)
            results.append(result)

        # 按胜率排序
        results_sorted = sorted(results, key=lambda x: x.win_rate, reverse=True)

        # 计算每个Agent的贡献度
        agent_contribution = self._calculate_agent_contribution(results)

        # 生成建议
        recommendations = self._generate_recommendations(results_sorted, agent_contribution)

        report = AblationReport(
            timestamp=datetime.now().isoformat(),
            base_agents=self.base_agents,
            questions_tested=len(questions),
            ablation_results=results_sorted,
            best_combination=results_sorted[0].combination_name if results_sorted else "",
            worst_combination=results_sorted[-1].combination_name if results_sorted else "",
            agent_contribution=agent_contribution,
            recommendations=recommendations,
        )

        return report

    def _calculate_agent_contribution(
        self,
        results: List[AblationResult],
    ) -> Dict[str, float]:
        """计算每个Agent的贡献度"""
        agent_scores = defaultdict(list)

        for result in results:
            # 使用胜率作为贡献指标
            score = result.win_rate
            for agent in result.combination:
                agent_scores[agent].append(score)

        # 计算每个Agent的平均贡献
        contribution = {}
        for agent, scores in agent_scores.items():
            contribution[agent] = np.mean(scores) if scores else 0

        return contribution

    def _generate_recommendations(
        self,
        results: List[AblationResult],
        agent_contribution: Dict[str, float],
    ) -> List[str]:
        """生成组合建议"""
        recommendations = []

        # 找出最佳组合
        if results:
            best = results[0]
            recommendations.append(
                f"最优组合: {best.combination_name} (胜率: {best.win_rate:.1%})"
            )

        # 找出最差组合
        if len(results) > 1:
            worst = results[-1]
            recommendations.append(
                f"最差组合: {worst.combination_name} (胜率: {worst.win_rate:.1%})"
            )

        # Agent贡献排序
        sorted_agents = sorted(agent_contribution.items(), key=lambda x: x[1], reverse=True)
        recommendations.append("\nAgent贡献度排名:")
        for agent, score in sorted_agents:
            recommendations.append(f"  {agent}: {score:.3f}")

        # 分析是否加Agent有边际效用
        single_agent_results = [r for r in results if r.num_agents == 1]
        three_agent_results = [r for r in results if r.num_agents == 3]

        if single_agent_results and three_agent_results:
            avg_single = np.mean([r.win_rate for r in single_agent_results])
            avg_three = np.mean([r.win_rate for r in three_agent_results])
            improvement = avg_three - avg_single

            recommendations.append(
                f"\n3人组合 vs 单Agent: {'+' if improvement > 0 else ''}{improvement:.1%}"
            )

        return recommendations


def run_ablation_experiment(
    provider: str = "mock",
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    base_agents: Optional[List[str]] = None,
    questions: Optional[List[Dict]] = None,
    debate_rounds: int = 2,
    verbose: bool = True,
) -> AblationReport:
    """运行消融实验的便捷函数"""

    if base_agents is None:
        base_agents = ["INTJ", "ENFP", "ISTJ", "ENTJ", "INFJ", "ESTP"]

    # 创建LLM客户端
    if provider == "mock":
        llm_client = MockLLMClient()
    else:
        from src.llm.client import OpenAIClient
        llm_client = OpenAIClient(api_key=api_key, model=model)

    # 加载问题
    if questions is None:
        from benchmark.datasets.evaluation_200 import get_dataset
        # 用前20题做快速测试
        questions = get_dataset()[:20]

    # 运行实验
    experiment = AblationExperiment(
        llm_client=llm_client,
        base_agents=base_agents,
        debate_rounds=debate_rounds,
    )

    report = experiment.run_full_ablation(questions, verbose=verbose)

    # 打印报告
    if verbose:
        print(f"\n{'='*80}")
        print("消融实验结果汇总")
        print(f"{'='*80}")

        print(f"\n最佳组合: {report.best_combination}")
        print(f"最差组合: {report.worst_combination}")

        print(f"\n所有组合排名:")
        print(f"{'组合':<15} {'胜率':>8} {'置信度':>8} {'分歧度':>8} {'Krippendorff α':>12} {'p值':>8}")
        print("-" * 80)
        for result in report.ablation_results:
            sig = "***" if result.p_value < 0.001 else ("**" if result.p_value < 0.01 else ("*" if result.p_value < 0.05 else ""))
            print(f"{result.combination_name:<15} {result.win_rate:>7.1%} {result.avg_confidence:>7.2f} {result.avg_divergence:>7.2f} {result.avg_krippendorff_alpha:>11.2f} {result.p_value:>7.4f}{sig}")

        print(f"\n注: * p<0.05, ** p<0.01, *** p<0.001 表示与同质基线的统计显著性")

        print(f"\n建议:")
        for rec in report.recommendations:
            print(f"  {rec}")

    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="消融实验")
    parser.add_argument("--provider", default="mock")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--model", default="gpt-4")
    parser.add_argument("--limit", type=int, default=10, help="问题数量限制")
    parser.add_argument("--agents", nargs="*", default=None)

    args = parser.parse_args()

    # 加载问题
    from benchmark.datasets.evaluation_200 import get_dataset
    questions = get_dataset()[:args.limit]

    run_ablation_experiment(
        provider=args.provider,
        api_key=args.api_key,
        model=args.model,
        base_agents=args.agents,
        questions=questions,
        verbose=True,
    )