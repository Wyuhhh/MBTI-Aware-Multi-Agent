"""
MBTI Agent基类
每个Agent对应一种MBTI性格类型
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

from ..mbti_prompts.personalities import MBTI_PERSONALITIES, MBTIPersonality
from ..llm.client import LLMClient


class MessageType(Enum):
    """消息类型"""
    INITIAL = "initial"           # 初始陈述
    CHALLENGE = "challenge"       # 挑战
    RESPONSE = "response"         # 回应挑战
    VOTE = "vote"                 # 投票
    VALIDATION = "validation"     # 性格校验


@dataclass
class AgentMessage:
    """Agent消息"""
    agent_id: str
    mbti_type: str
    content: str
    confidence: float = 0.5
    round: int = 0
    message_type: MessageType = MessageType.INITIAL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "mbti_type": self.mbti_type,
            "content": self.content,
            "confidence": self.confidence,
            "round": self.round,
            "message_type": self.message_type.value,
            "metadata": self.metadata,
        }


@dataclass
class MBTIAnalysis:
    """MBTI分析结果"""
    dimension: str  # T-F, N-S, J-P, E-I
    leaning: str    # e.g., "T", "F"
    confidence: float
    reasoning: str


class MBTIAgent:
    """MBTI性格Agent"""

    def __init__(
        self,
        mbti_type: str,
        llm_client: LLMClient,
        agent_id: Optional[str] = None,
        temperature: float = 0.7,
    ):
        if mbti_type not in MBTI_PERSONALITIES:
            raise ValueError(f"Unknown MBTI type: {mbti_type}")

        self.mbti_type = mbti_type
        self.agent_id = agent_id or f"{mbti_type}_{id(self)}"
        self.llm_client = llm_client
        self.temperature = temperature

        self.personality: MBTIPersonality = MBTI_PERSONALITIES[mbti_type]
        self.conversation_history: List[AgentMessage] = []

    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        dims = self.mbti_type
        e_i = "E" if "E" in dims else "I"
        n_s = "N" if "N" in dims else "S"
        t_f = "T" if "T" in dims else "F"
        j_p = "J" if "J" in dims else "P"

        prompt = f"""你正在扮演一个{self.personality.name}（MBTI类型：{self.mbti_type}）。

## 你的核心性格特征
{chr(10).join(f"- {trait}" for trait in self.personality.core_traits)}

## MBTI维度解读
- 能量方向：{'外向 (Extraversion) - 从外部世界获取能量' if e_i == 'E' else '内向 (Introversion) - 从内部世界获取能量'}
- 信息收集：{'直觉 (iNtuition) - 关注可能性和未来' if n_s == 'N' else '实感 (Sensing) - 关注具体事实和当下'}
- 决策方式：{'思考 (Thinking) - 基于逻辑和分析做决策' if t_f == 'T' else '情感 (Feeling) - 基于价值观和他人影响做决策'}
- 生活态度：{'判断 (Judging) - 喜欢结构和确定性' if j_p == 'J' else '感知 (Perceiving) - 喜欢灵活性和开放选项'}

## 性格描述
{self.personality.description}

## 沟通风格
{self.personality.communication_style}

## 决策方式
{self.personality.decision_making}

## 处理冲突的方式
{self.personality.conflict_handling}

## Few-shot示例
"""
        for i, example in enumerate(self.personality.few_shot_examples, 1):
            prompt += f"""
### 示例 {i}
**问题**: {example['Q']}
**回答**: {example['A']}
"""
        prompt += """

## 回答要求
1. 你的回答必须体现上述性格特征
2. 避免过于中立或八面玲珑，要有自己的立场
3. 用第一人称"我"来表达
4. 如果某些观点与你性格不符，明确指出
"""
        return prompt

    def think(self, query: str, round_num: int = 0) -> AgentMessage:
        """
        思考并生成回答
        """
        system_prompt = self._build_system_prompt()
        user_prompt = f"## 问题\n{query}\n\n## 要求\n请从你的MBTI性格角度给出回答，体现出你独特的思维方式和价值观。"

        response = self.llm_client.generate_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )

        # 提取置信度（如果有）
        confidence = self._extract_confidence(response)

        message = AgentMessage(
            agent_id=self.agent_id,
            mbti_type=self.mbti_type,
            content=response,
            confidence=confidence,
            round=round_num,
            message_type=MessageType.INITIAL,
        )
        self.conversation_history.append(message)
        return message

    def challenge(self, query: str, other_response: str, round_num: int) -> AgentMessage:
        """
        挑战其他Agent的观点
        """
        system_prompt = self._build_system_prompt()
        user_prompt = f"""## 问题
{query}

## 其他人的回答
{other_response}

## 任务
从你的{self.mbti_type}性格角度，挑战上述回答中的观点。指出其局限性、逻辑漏洞或你不同意的方面。保持角色特点，用第一人称表达。"""

        response = self.llm_client.generate_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )

        message = AgentMessage(
            agent_id=self.agent_id,
            mbti_type=self.mbti_type,
            content=response,
            confidence=0.5,
            round=round_num,
            message_type=MessageType.CHALLENGE,
        )
        self.conversation_history.append(message)
        return message

    def respond_to_challenge(
        self, query: str, challenge: str, round_num: int
    ) -> AgentMessage:
        """
        回应挑战
        """
        system_prompt = self._build_system_prompt()
        user_prompt = f"""## 问题
{query}

## 其他人对你的挑战
{challenge}

## 任务
从你的{self.mbti_type}性格角度，回应上述挑战。你可以：1) 坚持你的观点并给出更多论据；2) 承认对方有道理并调整你的观点；3) 提出新的综合观点。保持角色特点，用第一人称表达。"""

        response = self.llm_client.generate_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )

        # 更新置信度
        confidence = self._extract_confidence(response)

        message = AgentMessage(
            agent_id=self.agent_id,
            mbti_type=self.mbti_type,
            content=response,
            confidence=confidence,
            round=round_num,
            message_type=MessageType.RESPONSE,
        )
        self.conversation_history.append(message)
        return message

    def vote(
        self, query: str, all_responses: List[str], round_num: int
    ) -> AgentMessage:
        """
        对所有回答进行投票
        """
        system_prompt = self._build_system_prompt()
        responses_text = "\n\n".join(
            f"### 回答 {i+1}\n{resp}" for i, resp in enumerate(all_responses)
        )
        user_prompt = f"""## 问题
{query}

## 所有回答
{responses_text}

## 任务
从你的{self.mbti_type}性格角度，选择你认为最好的回答并说明理由。如果没有满意的，可以提出综合观点。最后给出你的最终选择（用编号）。"""

        response = self.llm_client.generate_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )

        message = AgentMessage(
            agent_id=self.agent_id,
            mbti_type=self.mbti_type,
            content=response,
            confidence=0.5,
            round=round_num,
            message_type=MessageType.VOTE,
        )
        self.conversation_history.append(message)
        return message

    def validate(self) -> bool:
        """
        性格校验：确保Agent没有偏离角色
        """
        questions_text = "\n".join(
            f"- {q}" for q in self.personality.validation_questions
        )
        user_prompt = f"""请诚实回答以下问题来确认你保持了{self.mbti_type}的角色特点：

{questions_text}

回答格式：简要说明你的回答是否符合{self.mbti_type}性格。"""

        system_prompt = self._build_system_prompt()
        response = self.llm_client.generate_with_messages(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )

        # 简单判断：如果回答中包含"符合"等正面词汇则认为通过
        return "符合" in response or "一致" in response or "是" in response

    def _extract_confidence(self, response: str) -> float:
        """
        从回答中提取置信度
        简单实现：检查是否有明确的置信度表述
        """
        import re

        # 尝试匹配置信度表述
        patterns = [
            r"置信度[是为：:]*\s*(\d+\.?\d*)",
            r"confidence[为：:]*\s*(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*%\s*置信",
            r"我有\s*(\d+\.?\d*)\s*分把握",
        ]

        for pattern in patterns:
            match = re.search(pattern, response)
            if match:
                value = float(match.group(1))
                if value > 1:
                    value = value / 100
                return min(max(value, 0.0), 1.0)

        # 默认置信度
        return 0.5

    def get_dimension_analysis(self) -> List[MBTIAnalysis]:
        """获取该Agent在各MBTI维度上的分析"""
        dims = self.mbti_type
        return [
            MBTIAnalysis(
                dimension="E-I",
                leaning=dims[0],
                confidence=0.8,
                reasoning=f"{'外向型偏好' if dims[0] == 'E' else '内向型偏好'}：从{self.personality.core_traits[0]}可以看出",
            ),
            MBTIAnalysis(
                dimension="N-S",
                leaning=dims[1],
                confidence=0.8,
                reasoning=f"{'直觉型偏好' if dims[1] == 'N' else '实感型偏好'}：关注{self.personality.core_traits[1] if len(self.personality.core_traits) > 1 else '具体事实'}",
            ),
            MBTIAnalysis(
                dimension="T-F",
                leaning=dims[2],
                confidence=0.8,
                reasoning=f"{'思考型偏好' if dims[2] == 'T' else '情感型偏好'}：{self.personality.decision_making[:20]}",
            ),
            MBTIAnalysis(
                dimension="J-P",
                leaning=dims[3],
                confidence=0.8,
                reasoning=f"{'判断型偏好' if dims[3] == 'J' else '感知型偏好'}：{self.personality.conflict_handling[:20]}",
            ),
        ]

    def reset(self):
        """重置对话历史"""
        self.conversation_history = []