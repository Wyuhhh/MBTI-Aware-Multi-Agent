"""
多维仲裁器
处理T-F、N-S、J-P维度的冲突
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum

from .base import MBTIAgent, AgentMessage, MBTIAnalysis


class ConflictDimension(Enum):
    """冲突维度"""
    TF = "T-F"  # Thinking vs Feeling
    NS = "N-S"  # Intuition vs Sensing
    JP = "J-P"  # Judging vs Perceiving
    EI = "E-I"  # Extraversion vs Introversion


@dataclass
class DimensionConflict:
    """单个维度的冲突"""
    dimension: ConflictDimension
    thinking_side: List[AgentMessage]  # T/N/J 方
    feeling_side: List[AgentMessage]   # F/S/P 方
    reasoning_chain: str = ""
    empathy_examples: List[str] = field(default_factory=list)
    synthesis: str = ""


@dataclass
class ArbitrationResult:
    """仲裁结果"""
    consensus: str
    alternatives: List[str]  # 开放选项列表
    reasoning_chain: str     # 逻辑论证链
    empathy_examples: List[str]  # 共情例证
    confidence: float
    dimension_analysis: Dict[str, str]  # 各维度分析
    final_summary: str = ""
    conflicts: List[DimensionConflict] = field(default_factory=list)


class MultiDimensionArbitrator:
    """多维仲裁器"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def arbitrate(
        self,
        agents: List[MBTIAgent],
        messages: List[AgentMessage],
        query: str,
    ) -> ArbitrationResult:
        """
        执行仲裁

        Args:
            agents: 参与仲裁的Agent列表
            messages: 所有消息
            query: 原始问题

        Returns:
            ArbitrationResult: 仲裁结果
        """
        # 分析各Agent的MBTI维度
        dimension_agents = self._group_by_dimension(agents)

        # 检测冲突
        conflicts = self._detect_conflicts(dimension_agents, messages)

        # 分诊处理
        consensus, alternatives = self._triage_and_resolve(
            conflicts, agents, messages, query
        )

        # 生成逻辑链和共情例证
        reasoning_chain = self._build_reasoning_chain(conflicts, agents)
        empathy_examples = self._extract_empathy_examples(conflicts, agents)

        # 各维度分析
        dimension_analysis = self._analyze_dimensions(agents, messages)

        # 计算置信度
        confidence = self._calculate_confidence(messages)

        return ArbitrationResult(
            consensus=consensus,
            alternatives=alternatives,
            reasoning_chain=reasoning_chain,
            empathy_examples=empathy_examples,
            confidence=confidence,
            dimension_analysis=dimension_analysis,
            conflicts=conflicts,
            final_summary=self._generate_summary(
                consensus, alternatives, reasoning_chain, empathy_examples
            ),
        )

    def _group_by_dimension(
        self, agents: List[MBTIAgent]
    ) -> Dict[str, List[MBTIAgent]]:
        """按MBTI维度分组"""
        groups = {
            "thinking": [],  # T
            "feeling": [],   # F
            "intuition": [], # N
            "sensing": [],   # S
            "judging": [],   # J
            "perceiving": [], # P
        }

        for agent in agents:
            dims = agent.mbti_type
            if "T" in dims:
                groups["thinking"].append(agent)
            if "F" in dims:
                groups["feeling"].append(agent)
            if "N" in dims:
                groups["intuition"].append(agent)
            if "S" in dims:
                groups["sensing"].append(agent)
            if "J" in dims:
                groups["judging"].append(agent)
            if "P" in dims:
                groups["perceiving"].append(agent)

        return groups

    def _detect_conflicts(
        self,
        dimension_agents: Dict[str, List[MBTIAgent]],
        messages: List[AgentMessage],
    ) -> List[DimensionConflict]:
        """检测维度冲突"""
        conflicts = []

        # T-F 冲突检测
        if dimension_agents["thinking"] and dimension_agents["feeling"]:
            thinking_msgs = self._get_agent_messages(
                dimension_agents["thinking"], messages
            )
            feeling_msgs = self._get_agent_messages(
                dimension_agents["feeling"], messages
            )
            if thinking_msgs and feeling_msgs:
                conflicts.append(
                    DimensionConflict(
                        dimension=ConflictDimension.TF,
                        thinking_side=thinking_msgs,
                        feeling_side=feeling_msgs,
                    )
                )

        # N-S 冲突检测
        if dimension_agents["intuition"] and dimension_agents["sensing"]:
            intuition_msgs = self._get_agent_messages(
                dimension_agents["intuition"], messages
            )
            sensing_msgs = self._get_agent_messages(
                dimension_agents["sensing"], messages
            )
            if intuition_msgs and sensing_msgs:
                conflicts.append(
                    DimensionConflict(
                        dimension=ConflictDimension.NS,
                        thinking_side=intuition_msgs,
                        feeling_side=sensing_msgs,
                    )
                )

        # J-P 冲突检测
        if dimension_agents["judging"] and dimension_agents["perceiving"]:
            judging_msgs = self._get_agent_messages(
                dimension_agents["judging"], messages
            )
            perceiving_msgs = self._get_agent_messages(
                dimension_agents["perceiving"], messages
            )
            if judging_msgs and perceiving_msgs:
                conflicts.append(
                    DimensionConflict(
                        dimension=ConflictDimension.JP,
                        thinking_side=judging_msgs,
                        feeling_side=perceiving_msgs,
                    )
                )

        return conflicts

    def _get_agent_messages(
        self, agents: List[MBTIAgent], all_messages: List[AgentMessage]
    ) -> List[AgentMessage]:
        """获取Agent的消息"""
        result = []
        for agent in agents:
            agent_msgs = [m for m in all_messages if m.agent_id == agent.agent_id]
            if agent_msgs:
                result.append(agent_msgs[-1])  # 取最新消息
        return result

    def _triage_and_resolve(
        self,
        conflicts: List[DimensionConflict],
        agents: List[MBTIAgent],
        messages: List[AgentMessage],
        query: str,
    ) -> Tuple[str, List[str]]:
        """
        分诊并解决冲突

        根据冲突类型采用不同策略：
        - T-F: 逻辑Agent给论证链，感性Agent给共情例证，合并输出
        - N-S: 实感派先查证据，直觉派给推演，最后整合
        - J-P: 判断派给确定性结论，感知派给开放选项，并列呈现
        """
        if not conflicts:
            # 无冲突，返回最后一条消息作为共识
            if messages:
                return messages[-1].content, []
            return "", []

        consensus_parts = []
        alternatives = []

        for conflict in conflicts:
            if conflict.dimension == ConflictDimension.TF:
                # T-F 冲突：合并逻辑和情感
                logic_part = self._synthesize_logic(conflict)
                empathy_part = self._synthesize_empathy(conflict)
                consensus_parts.append(f"**理性分析**: {logic_part}")
                consensus_parts.append(f"**情感视角**: {empathy_part}")
                conflict.reasoning_chain = logic_part
                conflict.empathy_examples = [empathy_part]

            elif conflict.dimension == ConflictDimension.NS:
                # N-S 冲突：整合直觉和实感
                synthesis = self._synthesize_ns(conflict)
                consensus_parts.append(f"**综合视角**: {synthesis}")
                conflict.synthesis = synthesis

                # 实感派给出务实选项
                sensing_options = self._extract_practical_options(conflict)
                alternatives.extend(sensing_options)

            elif conflict.dimension == ConflictDimension.JP:
                # J-P 冲突：并列呈现确定性和开放选项
                definite_conclusion = self._synthesize_judgment(conflict)
                open_options = self._synthesize_perceiving(conflict)
                consensus_parts.append(f"**确定性结论**: {definite_conclusion}")
                alternatives.append(f"**开放选项**: {open_options}")
                conflict.synthesis = f"{definite_conclusion} / {open_options}"

        consensus = "\n\n".join(consensus_parts)
        return consensus, alternatives

    def _synthesize_logic(self, conflict: DimensionConflict) -> str:
        """综合逻辑侧的观点"""
        logic_texts = [msg.content for msg in conflict.thinking_side]
        if not logic_texts:
            return ""
        # 简化：取第一条作为逻辑链
        return logic_texts[0][:500] + "..." if len(logic_texts[0]) > 500 else logic_texts[0]

    def _synthesize_empathy(self, conflict: DimensionConflict) -> str:
        """综合情感侧的观点"""
        feeling_texts = [msg.content for msg in conflict.feeling_side]
        if not feeling_texts:
            return ""
        return feeling_texts[0][:500] + "..." if len(feeling_texts[0]) > 500 else feeling_texts[0]

    def _synthesize_ns(self, conflict: DimensionConflict) -> str:
        """综合直觉和实感的观点"""
        intuition_texts = [msg.content for msg in conflict.thinking_side]
        sensing_texts = [msg.content for msg in conflict.feeling_side]

        parts = []
        if intuition_texts:
            parts.append(f"直觉视角: {intuition_texts[0][:200]}...")
        if sensing_texts:
            parts.append(f"实感视角: {sensing_texts[0][:200]}...")

        return " | ".join(parts)

    def _extract_practical_options(self, conflict: DimensionConflict) -> List[str]:
        """提取务实选项"""
        options = []
        for msg in conflict.feeling_side:
            # 简化：取消息的前200字符作为选项
            option = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
            options.append(option)
        return options

    def _synthesize_judgment(self, conflict: DimensionConflict) -> str:
        """综合判断派的观点"""
        judging_texts = [msg.content for msg in conflict.thinking_side]
        if not judging_texts:
            return ""
        return judging_texts[0][:300] + "..." if len(judging_texts[0]) > 300 else judging_texts[0]

    def _synthesize_perceiving(self, conflict: DimensionConflict) -> str:
        """综合感知派的观点"""
        perceiving_texts = [msg.content for msg in conflict.feeling_side]
        if not perceiving_texts:
            return ""
        return perceiving_texts[0][:300] + "..." if len(perceiving_texts[0]) > 300 else perceiving_texts[0]

    def _build_reasoning_chain(
        self, conflicts: List[DimensionConflict], agents: List[MBTIAgent]
    ) -> str:
        """构建逻辑论证链"""
        lines = ["## 论证链\n"]

        # 从conflicts中提取thinking_side的消息来构建论证链
        for conflict in conflicts:
            for msg in conflict.thinking_side:
                lines.append(f"**{msg.mbti_type}**: {msg.content[:150]}...")
            for msg in conflict.feeling_side:
                lines.append(f"**{msg.mbti_type}**: {msg.content[:150]}...")

        return "\n".join(lines)

    def _extract_empathy_examples(
        self, conflicts: List[DimensionConflict], agents: List[MBTIAgent]
    ) -> List[str]:
        """提取共情例证"""
        examples = []
        for conflict in conflicts:
            if conflict.dimension == ConflictDimension.TF:
                for msg in conflict.feeling_side:
                    examples.append(msg.content[:200])
        return examples

    def _analyze_dimensions(
        self, agents: List[MBTIAgent], messages: List[AgentMessage]
    ) -> Dict[str, str]:
        """分析各维度"""
        analysis = {}
        for agent in agents:
            dims = agent.mbti_type
            if "T" in dims:
                analysis["T-F"] = analysis.get("T-F", "") + f"{agent.mbti_type}倾向思考, "
            if "F" in dims:
                analysis["T-F"] = analysis.get("T-F", "") + f"{agent.mbti_type}倾向情感, "
            if "N" in dims:
                analysis["N-S"] = analysis.get("N-S", "") + f"{agent.mbti_type}倾向直觉, "
            if "S" in dims:
                analysis["N-S"] = analysis.get("N-S", "") + f"{agent.mbti_type}倾向实感, "
            if "J" in dims:
                analysis["J-P"] = analysis.get("J-P", "") + f"{agent.mbti_type}倾向判断, "
            if "P" in dims:
                analysis["J-P"] = analysis.get("J-P", "") + f"{agent.mbti_type}倾向感知, "
        return analysis

    def _calculate_confidence(self, messages: List[AgentMessage]) -> float:
        """计算置信度"""
        if not messages:
            return 0.0

        # 简单平均
        confidences = [m.confidence for m in messages]
        return sum(confidences) / len(confidences)

    def _generate_summary(
        self,
        consensus: str,
        alternatives: List[str],
        reasoning_chain: str,
        empathy_examples: List[str],
    ) -> str:
        """生成最终总结"""
        lines = ["# 仲裁结果\n"]

        if consensus:
            lines.append("## 共识\n" + consensus)

        if alternatives:
            lines.append("\n## 替代选项\n" + "\n".join(f"- {alt}" for alt in alternatives))

        if reasoning_chain:
            lines.append("\n" + reasoning_chain)

        return "\n".join(lines)