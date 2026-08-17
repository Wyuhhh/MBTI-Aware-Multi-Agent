"""
测试多维仲裁器
"""

import pytest
from src.agent.arbitrator import (
    MultiDimensionArbitrator,
    ArbitrationResult,
    DimensionConflict,
    ConflictDimension,
)
from src.agent.base import MBTIAgent, AgentMessage, MessageType
from src.llm.client import MockLLMClient


@pytest.fixture
def mock_llm_client():
    """创建Mock LLM客户端"""
    return MockLLMClient(response="Mock response")


@pytest.fixture
def sample_agents(mock_llm_client):
    """创建样例Agents"""
    return [
        MBTIAgent("INTJ", mock_llm_client, agent_id="test_INTJ"),
        MBTIAgent("ENFP", mock_llm_client, agent_id="test_ENFP"),
        MBTIAgent("ISTJ", mock_llm_client, agent_id="test_ISTJ"),
    ]


def test_arbitrator_initialization():
    """测试仲裁器初始化"""
    arbitrator = MultiDimensionArbitrator()
    assert arbitrator.llm_client is None


def test_arbitrate_returns_result(sample_agents):
    """测试仲裁返回正确的结果结构"""
    arbitrator = MultiDimensionArbitrator()
    messages = [
        AgentMessage(
            agent_id="test_INTJ",
            mbti_type="INTJ",
            content="Test content 1",
            confidence=0.7,
        ),
        AgentMessage(
            agent_id="test_ENFP",
            mbti_type="ENFP",
            content="Test content 2",
            confidence=0.6,
        ),
    ]

    result = arbitrator.arbitrate(
        agents=sample_agents,
        messages=messages,
        query="测试问题",
    )

    assert isinstance(result, ArbitrationResult)
    assert hasattr(result, "consensus")
    assert hasattr(result, "alternatives")
    assert hasattr(result, "reasoning_chain")
    assert hasattr(result, "empathy_examples")
    assert hasattr(result, "confidence")


def test_dimension_analysis(sample_agents):
    """测试维度分析"""
    arbitrator = MultiDimensionArbitrator()
    messages = []

    result = arbitrator.arbitrate(
        agents=sample_agents,
        messages=messages,
        query="测试问题",
    )

    assert isinstance(result.dimension_analysis, dict)


def test_confidence_calculation():
    """测试置信度计算"""
    arbitrator = MultiDimensionArbitrator()
    messages = [
        AgentMessage("a", "INTJ", "", confidence=0.8),
        AgentMessage("b", "ENFP", "", confidence=0.6),
        AgentMessage("c", "ISTJ", "", confidence=0.7),
    ]

    result = arbitrator.arbitrate(
        agents=[],
        messages=messages,
        query="测试",
    )

    expected_confidence = (0.8 + 0.6 + 0.7) / 3
    assert abs(result.confidence - expected_confidence) < 0.01