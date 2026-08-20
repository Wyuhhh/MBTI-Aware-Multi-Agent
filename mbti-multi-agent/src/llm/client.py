"""
LLM客户端封装
支持OpenAI GPT和Anthropic Claude
"""

import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
import json


class LLMClient(ABC):
    """LLM客户端抽象基类"""

    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """生成回复"""
        pass

    @abstractmethod
    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        """多轮对话生成"""
        pass

    def _parse_json_safe(self, text: str) -> Optional[Dict]:
        """安全解析JSON"""
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取代码块
        import re
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试提取花括号内容
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None


class OpenAIClient(LLMClient):
    """OpenAI GPT客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        base_url: Optional[str] = None,
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")

        self.model = model
        self.client = OpenAI(api_key=self.api_key, base_url=base_url)

    def _parse_response(self, response) -> str:
        """解析OpenAI响应"""
        if not response.choices:
            return ""
        content = response.choices[0].message.content
        return content if content else ""

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return self._parse_response(response)
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return self._parse_response(response)
        except Exception as e:
            return f"Error: {str(e)}"


class AnthropicClient(LLMClient):
    """Anthropic Claude客户端（兼容MiniMax Anthropic格式）"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        base_url: Optional[str] = None,
    ):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")

        self.model = model
        self.client = Anthropic(api_key=self.api_key, base_url=base_url)

    def _parse_response(self, response) -> str:
        """解析Anthropic响应，跳过thinking块"""
        for block in response.content:
            if hasattr(block, 'type') and block.type == "text":
                return block.text
        # 如果没有text块，返回空
        return ""

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """转换消息格式以适配Anthropic API"""
        converted = []
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "assistant"
            content = msg.get("content", "")
            # 如果content是字符串，直接使用；如果是列表，转为字符串
            if isinstance(content, list):
                content = " ".join([c.get("text", str(c)) if isinstance(c, dict) else str(c) for c in content])
            converted.append({"role": role, "content": content})
        return converted

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_response(response)
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        try:
            claude_messages = self._convert_messages(messages)
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=claude_messages,
            )
            return self._parse_response(response)
        except Exception as e:
            return f"Error: {str(e)}"


class MiniMaxClient(LLMClient):
    """MiniMax模型客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "MiniMax-M2.7",
        base_url: Optional[str] = None,
    ):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("MINIMAX_API_KEY") or "sk-1234"
        self.model = model

        # 默认使用内网代理地址
        self.base_url = base_url or os.getenv("MINIMAX_BASE_URL") or "http://10.68.46.180:31943"

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


class MockLLMClient(LLMClient):
    """用于测试的Mock客户端，返回随机但合理的响应"""

    # 不同MBTI类型的模拟响应风格
    MBTI_RESPONSES = {
        "INTJ": [
            "从战略角度分析，这个问题需要考虑长期影响。最佳方案是制定分阶段计划，明确里程碑。",
            "逻辑推导表明，我们需要权衡成本与收益。我的建议是采用渐进式策略。",
            "理性分析：这个问题有多个变量需要考虑。建议从核心问题入手，逐步解决。",
        ],
        "INTP": [
            "这是一个有趣的悖论。让我从理论角度分析...核心在于理解底层机制。",
            "从抽象角度看，这个问题的本质是信息不对称。建议建立有效的反馈循环。",
            "逻辑上，这个问题可以分解为几个子问题。每个子问题都需要独立验证。",
        ],
        "ENTJ": [
            "直接说重点：我们需要果断决策。机会窗口有限，必须立即行动。",
            "高效解决方案：立即成立专项小组，设定明确KPI，两周内拿出结果。",
            "我的判断是，这个决定不能拖延。执行力和速度是关键竞争优势。",
        ],
        "ENTP": [
            "等等，这个问题有更好的解法！让我挑战一下前提假设...",
            "如果从另一个角度看呢？创新机会就在这里——打破常规思维。",
            "我觉得这个问题被过度复杂化了。简单有效的方案往往最优。",
        ],
        "INFJ": [
            "我能理解你的感受。这个决定对你来说很重要，因为它关乎你的价值观。",
            "从人文角度，我建议考虑所有相关人员的感受和需求。共赢才是真正的胜利。",
            "这个选择不仅仅是理性的判断，也关乎你内心的声音。追随你的价值观。",
        ],
        "INFP": [
            "我相信每个选择都应该符合内心的原则。请先思考：什么对你来说最重要？",
            "这个问题没有唯一正确答案，关键是找到与你的价值观一致的路径。",
            "从理想主义角度，我建议追求一个能让你感到意义和满足的目标。",
        ],
        "ENFJ": [
            "我相信团队的力量！让我们一起找到共识，激励每个人发挥最大潜能。",
            "从人际角度，关键是要理解每个人的动机和需求。建立信任是第一步。",
            "我的建议是：先凝聚共识，再制定行动计划。共同愿景比强制服从更有力。",
        ],
        "ENFP": [
            "哇，这个可能性太令人兴奋了！让我们探索所有创新的可能性！",
            "如果大胆尝试一下呢？life is short, let's take risks!",
            "我看到了很多有趣的方向！让我们头脑风暴，找到最有创意的解决方案。",
        ],
        "ISTJ": [
            "根据历史数据和现有规范，我建议遵循既定流程。稳定性和可预测性很重要。",
            "务实分析：最可靠的方案是参考成功案例，逐步推进，避免风险。",
            "我的建议是：先收集完整信息，再做决定。数据和事实胜于主观判断。",
        ],
        "ISFJ": [
            "我会确保每个人的需求都被照顾到。细节很重要，关怀也很重要。",
            "从历史经验看，稳妥的方案是渐进式改进。循序渐进，避免激进变革。",
            "我关心的是：这个决定对团队成员会有什么影响？他们的感受很重要。",
        ],
        "ESTJ": [
            "效率第一！让我们制定清晰的计划，按流程执行，及时跟踪结果。",
            "事实说话：我建议立即行动，设定deadline，责任到人。",
            "我的判断基于数据和经验。执行计划需要纪律和责任感。",
        ],
        "ESFJ": [
            "让我们确保每个人都满意！团队和谐很重要，我会照顾到每个人的感受。",
            "从人际角度，我建议先沟通再执行。共识和协作能带来更好的结果。",
            "我相信通过耐心的沟通和协调，我们能找到大家都能接受的方案。",
        ],
        "ISTP": [
            "技术角度看，这个问题有更优雅的解决方案。让我展示给你看...",
            "实践出真知。与其理论分析，不如动手试试看实际效果。",
            "关键变量是XX和YY。简化问题，直击核心矛盾。",
        ],
        "ISFP": [
            "Life is beautiful. 让我们选择一个能带来和谐与美感的方案。",
            "我现在感受到的是... 跟随直觉，有时比过度分析更可靠。",
            "从审美角度，我倾向于选择一个更优雅、更自然的解决方式。",
        ],
        "ESTP": [
            "马上行动！机会稍纵即逝，我们现在就要抓住它。",
            "实战经验告诉我，最有效的方法是边做边学，快速迭代。",
            "不要想太多，干就完了！结果比过程重要。",
        ],
        "ESFP": [
            "太棒了！让我们让这件事变得有趣和令人兴奋！",
            "Life is a party! 让我们享受这个过程，同时把事情做成。",
            "从乐观角度，我相信一切都会有最好的结果。热情是最好的驱动力！",
        ],
    }

    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.call_count = 0
        self.last_prompt = None
        import random
        self._random = random

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        return self._generate_adaptive_response(prompt)

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        self.call_count += 1
        self.last_prompt = messages
        # 从消息中尝试检测MBTI类型
        mbti_type = self._detect_mbti_from_messages(messages)
        # 从消息中提取prompt
        prompt = " ".join([str(m.get("content", "")) for m in messages])
        return self._generate_mbti_response(mbti_type, prompt)

    def _generate_adaptive_response(self, prompt: str) -> str:
        """根据prompt内容生成更贴合的响应"""
        prompt_lower = prompt.lower()
        if "考研" in prompt or "工作" in prompt or "职业" in prompt:
            return self._random.choice([
                "这是一个关于职业规划的重要决定。需要综合考虑你的兴趣、能力和市场需求。",
                "从多个角度看，这个选择各有利弊。建议用pros/cons列表法分析。",
                "无论选择哪条路，关键是你能从中获得成长和满足感。",
            ])
        elif "伦理" in prompt or "道德" in prompt:
            return self._random.choice([
                "这是一个复杂的伦理问题，没有绝对的正确答案。",
                "从道德哲学角度，我们需要权衡不同伦理原则。",
                "这个困境反映了现实世界中价值观的冲突。",
            ])
        elif "技术" in prompt or "代码" in prompt:
            return self._random.choice([
                "从技术角度，有几种可行的实现方案。",
                "这个问题需要更详细的技术分析。",
                "建议采用模块化设计，便于后续维护和扩展。",
            ])
        else:
            return self._random.choice([
                "这是一个有趣的观点。让我从多个角度分析...",
                "综合考虑各种因素，我的建议是...",
                "基于目前的信息，我认为...",
            ])

    def _detect_mbti_from_messages(self, messages: List[Dict[str, str]]) -> str:
        """从消息中检测MBTI类型"""
        full_text = " ".join([str(m.get("content", "")) for m in messages])
        # 简单关键词匹配
        if "战略" in full_text or "长期" in full_text:
            return "INTJ"
        elif "创新" in full_text or "可能性" in full_text:
            return "ENFP"
        elif "感受" in full_text or "价值" in full_text:
            return "INFJ"
        elif "执行" in full_text or "效率" in full_text:
            return "ESTJ"
        elif "数据" in full_text or "事实" in full_text:
            return "ISTJ"
        else:
            return "INTJ"  # 默认

    def _generate_mbti_response(self, mbti_type: str, prompt: str = "") -> str:
        """生成符合MBTI类型的响应"""
        responses = self.MBTI_RESPONSES.get(mbti_type, self.MBTI_RESPONSES["INTJ"])
        return self._random.choice(responses)