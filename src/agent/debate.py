"""
辩论机制
管理多轮辩论流程
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .base import MBTIAgent, AgentMessage, MessageType


@dataclass
class DebateRound:
    """单轮辩论"""
    round_num: int
    initial_messages: List[AgentMessage] = field(default_factory=list)
    challenge_pairs: List[Tuple[AgentMessage, AgentMessage]] = field(default_factory=list)
    responses: List[AgentMessage] = field(default_factory=list)


@dataclass
class DebateResult:
    """辩论结果"""
    rounds: List[DebateRound]
    all_messages: List[AgentMessage]
    final_positions: Dict[str, str]  # agent_id -> final position
    convergence_achieved: bool
    summary: str


class DebateManager:
    """辩论管理器"""

    def __init__(self, max_rounds: int = 3):
        self.max_rounds = max_rounds
        self.debate_history: List[DebateRound] = []

    def run_debate(
        self,
        agents: List[MBTIAgent],
        query: str,
        max_rounds: Optional[int] = None,
    ) -> DebateResult:
        """
        运行多轮辩论

        Args:
            agents: 参与辩论的Agent列表
            query: 辩题/问题
            max_rounds: 最大轮数，默认使用初始化时的值

        Returns:
            DebateResult: 辩论结果
        """
        if max_rounds is None:
            max_rounds = self.max_rounds

        self.debate_history = []
        all_messages: List[AgentMessage] = []
        final_positions: Dict[str, str] = {}

        # 第一轮：初始陈述
        initial_messages = []
        for agent in agents:
            msg = agent.think(query, round_num=0)
            initial_messages.append(msg)
            all_messages.append(msg)

        current_round = DebateRound(round_num=0, initial_messages=initial_messages)
        self.debate_history.append(current_round)

        # 多轮挑战
        for round_num in range(1, max_rounds + 1):
            round_data = DebateRound(round_num=round_num)

            # 交叉挑战
            challenges = []
            for i, challenger in enumerate(agents):
                # 挑战其他Agent的观点
                other_idx = (i + 1) % len(agents)
                other_agent = agents[other_idx]
                other_messages = [m for m in all_messages if m.agent_id == other_agent.agent_id]
                other_response = other_messages[-1].content if other_messages else ""

                challenge_msg = challenger.challenge(query, other_response, round_num)
                challenges.append((challenge_msg, other_agent.agent_id))
                all_messages.append(challenge_msg)

                # 被挑战的Agent回应
                response_msg = other_agent.respond_to_challenge(
                    query, challenge_msg.content, round_num
                )
                round_data.responses.append(response_msg)
                all_messages.append(response_msg)

            round_data.challenge_pairs = challenges
            self.debate_history.append(round_data)

        # 收集最终立场
        for agent in agents:
            agent_messages = [m for m in all_messages if m.agent_id == agent.agent_id]
            if agent_messages:
                final_positions[agent.agent_id] = agent_messages[-1].content

        # 生成总结
        summary = self._generate_summary(agents, all_messages)

        return DebateResult(
            rounds=self.debate_history,
            all_messages=all_messages,
            final_positions=final_positions,
            convergence_achieved=self._check_convergence(all_messages),
            summary=summary,
        )

    def run_structured_debate(
        self,
        agents: List[MBTIAgent],
        query: str,
        max_rounds: int = 3,
    ) -> DebateResult:
        """
        运行结构化辩论（确保每个Agent都有机会挑战其他所有Agent）

        Args:
            agents: 参与辩论的Agent列表
            query: 辩题/问题
            max_rounds: 最大轮数

        Returns:
            DebateResult: 辩论结果
        """
        self.debate_history = []
        all_messages: List[AgentMessage] = []
        final_positions: Dict[str, str] = {}

        # 第一轮：初始陈述
        initial_messages = []
        for agent in agents:
            msg = agent.think(query, round_num=0)
            initial_messages.append(msg)
            all_messages.append(msg)

        self.debate_history.append(DebateRound(round_num=0, initial_messages=initial_messages))

        # 多轮交叉挑战
        for round_num in range(1, max_rounds + 1):
            round_data = DebateRound(round_num=round_num)

            # 每个Agent挑战每个其他Agent
            for i, challenger in enumerate(agents):
                for j, target in enumerate(agents):
                    if i == j:
                        continue

                    # 获取目标Agent的最新观点
                    target_messages = [m for m in all_messages if m.agent_id == target.agent_id]
                    target_response = target_messages[-1].content if target_messages else ""

                    # 发起挑战
                    challenge_msg = challenger.challenge(query, target_response, round_num)
                    all_messages.append(challenge_msg)

                    # 目标回应
                    response_msg = target.respond_to_challenge(
                        query, challenge_msg.content, round_num
                    )
                    round_data.responses.append(response_msg)
                    all_messages.append(response_msg)

            self.debate_history.append(round_data)

        # 收集最终立场
        for agent in agents:
            agent_messages = [m for m in all_messages if m.agent_id == agent.agent_id]
            if agent_messages:
                final_positions[agent.agent_id] = agent_messages[-1].content

        summary = self._generate_summary(agents, all_messages)

        return DebateResult(
            rounds=self.debate_history,
            all_messages=all_messages,
            final_positions=final_positions,
            convergence_achieved=self._check_convergence(all_messages),
            summary=summary,
        )

    def _generate_summary(self, agents: List[MBTIAgent], messages: List[AgentMessage]) -> str:
        """生成辩论总结"""
        summaries = []
        for agent in agents:
            agent_messages = [m for m in messages if m.agent_id == agent.agent_id]
            if agent_messages:
                last_msg = agent_messages[-1]
                summaries.append(
                    f"**{agent.mbti_type} ({agent.personality.name})**: "
                    f"{last_msg.content[:200]}..."
                )

        return "\n\n".join(summaries)

    def _check_convergence(self, messages: List[AgentMessage]) -> bool:
        """检查是否收敛（所有Agent的观点是否趋于一致）"""
        if len(messages) < 2:
            return False

        # 简化的收敛检查：比较最后几轮消息的语义相似度
        # 这里用置信度变化作为代理指标
        final_round = max(m.round for m in messages)
        final_messages = [m for m in messages if m.round == final_round]

        if len(final_messages) < 2:
            return False

        # 计算置信度方差
        confidences = [m.confidence for m in final_messages]
        avg_conf = sum(confidences) / len(confidences)
        variance = sum((c - avg_conf) ** 2 for c in confidences) / len(confidences)

        # 如果置信度接近，认为收敛
        return variance < 0.05

    def get_debate_flow(self) -> str:
        """获取辩论流程的文本描述"""
        lines = []
        for round_data in self.debate_history:
            lines.append(f"\n=== 第 {round_data.round_num} 轮 ===")
            if round_data.initial_messages:
                lines.append(f"初始陈述: {len(round_data.initial_messages)} 条")
            if round_data.challenge_pairs:
                lines.append(f"挑战对: {len(round_data.challenge_pairs)} 对")
            if round_data.responses:
                lines.append(f"回应: {len(round_data.responses)} 条")

        return "\n".join(lines)