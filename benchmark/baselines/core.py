"""
4组基线实现

1. HomogeneousBaseline: 同质Agent基线（3个相同MBTI类型）
2. RandomMBTIBaseline: 随机MBTI组合
3. SingleBestBaseline: 单Agent最佳(INTJ)
4. OracleBaseline: 理想基线(取所有Agent共识)
"""

import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agent.base import MBTIAgent
from src.agent.debate import DebateManager
from src.llm.client import LLMClient


@dataclass
class BaselineResult:
    """基线结果"""
    name: str
    agents_used: List[str]
    debate_rounds: int
    initial_responses: Dict[str, str]  # agent_id -> response
    final_consensus: str
    confidence: float
    metadata: Dict[str, Any]


class BaseBaseline(ABC):
    """基线抽象类"""

    def __init__(
        self,
        llm_client: LLMClient,
        name: str = "base",
        debate_rounds: int = 2,
    ):
        self.llm_client = llm_client
        self.name = name
        self.debate_rounds = debate_rounds
        self.debate_manager = DebateManager(max_rounds=debate_rounds)

    @abstractmethod
    def get_agent_types(self) -> List[str]:
        """返回使用的MBTI类型列表"""
        pass

    def run(self, query: str) -> BaselineResult:
        """运行基线"""
        mbti_types = self.get_agent_types()

        # 创建Agents
        agents = []
        for i, mbti_type in enumerate(mbti_types):
            agent = MBTIAgent(
                mbti_type=mbti_type,
                llm_client=self.llm_client,
                agent_id=f"{self.name}_{mbti_type}_{i}",
            )
            agents.append(agent)

        # 收集初始回应
        initial_responses = {}
        for agent in agents:
            msg = agent.think(query, round_num=0)
            initial_responses[agent.agent_id] = msg.content

        # 运行辩论
        debate_result = self.debate_manager.run_debate(
            agents=agents,
            query=query,
            max_rounds=self.debate_rounds,
        )

        # 汇总最终共识
        if debate_result.final_positions:
            final_consensus = self._aggregate_responses(
                list(debate_result.final_positions.values())
            )
        else:
            final_consensus = list(initial_responses.values())[0] if initial_responses else ""

        # 计算置信度
        confidences = [
            m.confidence for m in debate_result.all_messages
            if hasattr(m, 'confidence')
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.5

        return BaselineResult(
            name=self.name,
            agents_used=mbti_types,
            debate_rounds=self.debate_rounds,
            initial_responses=initial_responses,
            final_consensus=final_consensus,
            confidence=avg_confidence,
            metadata={
                "num_messages": len(debate_result.all_messages),
                "convergence_achieved": debate_result.convergence_achieved,
            },
        )

    def _aggregate_responses(self, responses: List[str]) -> str:
        """聚合多个回应为共识"""
        if not responses:
            return ""
        if len(responses) == 1:
            return responses[0]
        # 简化为直接拼接，实际可用更复杂方法
        return "\n\n---\n\n".join(responses[:3])


class HomogeneousBaseline(BaseBaseline):
    """
    同质Agent基线

    使用3个完全相同的MBTI类型，模拟"同质群智"问题
    预期：观点趋同，缺乏多样性视角
    """

    def __init__(
        self,
        llm_client: LLMClient,
        mbti_type: str = "INTJ",
        debate_rounds: int = 2,
    ):
        super().__init__(
            llm_client=llm_client,
            name=f"homogeneous_{mbti_type}",
            debate_rounds=debate_rounds,
        )
        self.mbti_type = mbti_type

    def get_agent_types(self) -> List[str]:
        return [self.mbti_type, self.mbti_type, self.mbti_type]


class RandomMBTIBaseline(BaseBaseline):
    """
    随机MBTI组合基线

    随机选择3个不同的MBTI类型，不考虑任务适配
    预期：结果不稳定，受随机性影响大
    """

    ALL_TYPES = [
        "INTJ", "INTP", "ENTJ", "ENTP",
        "INFJ", "INFP", "ENFJ", "ENFP",
        "ISTJ", "ISFJ", "ESTJ", "ESFJ",
        "ISTP", "ISFP", "ESTP", "ESFP",
    ]

    def __init__(
        self,
        llm_client: LLMClient,
        debate_rounds: int = 2,
        seed: Optional[int] = None,
    ):
        super().__init__(
            llm_client=llm_client,
            name="random_mbti",
            debate_rounds=debate_rounds,
        )
        if seed is not None:
            random.seed(seed)
        self.selected_types = random.sample(self.ALL_TYPES, 3)

    def get_agent_types(self) -> List[str]:
        return self.selected_types


class SingleBestBaseline(BaseBaseline):
    """
    单Agent最佳基线

    只使用单一最佳Agent(INTJ)，无辩论无聚合
    预期：反应快速但缺乏多视角
    """

    def __init__(
        self,
        llm_client: LLMClient,
        mbti_type: str = "INTJ",
    ):
        super().__init__(
            llm_client=llm_client,
            name=f"single_{mbti_type}",
            debate_rounds=0,  # 无辩论
        )
        self.mbti_type = mbti_type

    def get_agent_types(self) -> List[str]:
        return [self.mbti_type]

    def run(self, query: str) -> BaselineResult:
        """单Agent直接回答"""
        agent = MBTIAgent(
            mbti_type=self.mbti_type,
            llm_client=self.llm_client,
            agent_id=f"{self.name}_{self.mbti_type}_0",
        )

        msg = agent.think(query, round_num=0)

        return BaselineResult(
            name=self.name,
            agents_used=[self.mbti_type],
            debate_rounds=0,
            initial_responses={agent.agent_id: msg.content},
            final_consensus=msg.content,
            confidence=msg.confidence,
            metadata={"single_agent": True},
        )


class OracleBaseline(BaseBaseline):
    """
    理想基线 (Oracle)

    使用完整的INTJ+ENFP+ISTJ组合，所有辩论轮次
    代表"理论上最佳"的异质Agent协作效果
    用于衡量其他基线与最佳实践的差距
    """

    def __init__(
        self,
        llm_client: LLMClient,
        debate_rounds: int = 3,
    ):
        super().__init__(
            llm_client=llm_client,
            name="oracle",
            debate_rounds=debate_rounds,
        )

    def get_agent_types(self) -> List[str]:
        return ["INTJ", "ENFP", "ISTJ"]


# ============ 批量基线运行器 ============

class BaselineRunner:
    """批量运行所有基线"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def run_all_baselines(
        self,
        query: str,
        debate_rounds: int = 2,
    ) -> Dict[str, BaselineResult]:
        """运行所有4组基线"""
        results = {}

        # 1. 同质基线 (INTJ)
        print(f"  Running homogeneous_INTJ baseline...")
        baseline = HomogeneousBaseline(
            self.llm_client,
            mbti_type="INTJ",
            debate_rounds=debate_rounds,
        )
        results["homogeneous_INTJ"] = baseline.run(query)

        # 2. 随机MBTI
        print(f"  Running random_mbti baseline...")
        baseline = RandomMBTIBaseline(
            self.llm_client,
            debate_rounds=debate_rounds,
            seed=42,
        )
        results["random_mbti"] = baseline.run(query)

        # 3. 单Agent最佳
        print(f"  Running single_INTJ baseline...")
        baseline = SingleBestBaseline(
            self.llm_client,
            mbti_type="INTJ",
        )
        results["single_INTJ"] = baseline.run(query)

        # 4. Oracle (异质Agent最佳)
        print(f"  Running oracle baseline...")
        baseline = OracleBaseline(
            self.llm_client,
            debate_rounds=debate_rounds,
        )
        results["oracle"] = baseline.run(query)

        return results

    def compare_baselines(
        self,
        results: Dict[str, BaselineResult],
    ) -> Dict[str, Any]:
        """对比所有基线结果"""
        comparison = {
            "baseline_names": list(results.keys()),
            "agent_counts": {},
            "confidences": {},
            "consensus_lengths": {},
        }

        for name, result in results.items():
            comparison["agent_counts"][name] = len(result.agents_used)
            comparison["confidences"][name] = result.confidence
            comparison["consensus_lengths"][name] = len(result.final_consensus)

        return comparison