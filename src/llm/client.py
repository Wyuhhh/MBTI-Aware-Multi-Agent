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


class AnthropicClient(LLMClient):
    """Anthropic Claude客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
    ):
        try:
            from anthropic import Anthropic
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        # Convert messages format for Claude
        claude_messages = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            claude_messages.append({"role": role, "content": msg["content"]})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=claude_messages,
        )
        return response.content[0].text


class MockLLMClient(LLMClient):
    """用于测试的Mock客户端"""

    def __init__(self, response: str = "Mock response"):
        self.response = response
        self.call_count = 0
        self.last_prompt = None

    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        self.call_count += 1
        self.last_prompt = prompt
        return self.response

    def generate_with_messages(
        self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        self.call_count += 1
        self.last_prompt = messages
        return self.response