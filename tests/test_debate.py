"""
测试辩论机制
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.agent.base import MBTIAgent, AgentMessage, MessageType
from src.agent.debate import DebateManager, DebateResult, DebateRound
from src.llm.client import MockLLMClient


@pytest.fixture
def mock_llm_client():
    """创建Mock LLM客户端"""
    client = MockLLMClient(response="Mock response")
    return client


@pytest.fixture
def sample_agents(mock_llm_client):
    """创建样例Agents"""
    agents = [
        MBTIAgent("INTJ", mock_llm_client, agent_id="test_INTJ"),
        MBTIAgent("ENFP", mock_llm_client, agent_id="test_ENFP"),
    ]
    return agents


def test_debate_manager_initialization():
    """测试辩论管理器初始化"""
    manager = DebateManager(max_rounds=5)
    assert manager.max_rounds == 5
    assert manager.debate_history == []


def test_run_debate_returns_debate_result(sample_agents):
    """测试运行辩论返回正确的结果结构"""
    manager = DebateManager(max_rounds=2)
    result = manager.run_debate(
        agents=sample_agents,
        query="测试问题",
        max_rounds=2,
    )

    assert isinstance(result, DebateResult)
    assert isinstance(result.rounds, list)
    assert isinstance(result.all_messages, list)
    assert isinstance(result.final_positions, dict)
    assert isinstance(result.convergence_achieved, bool)


def test_run_debate_creates_messages(sample_agents):
    """测试辩论产生正确数量的消息"""
    manager = DebateManager(max_rounds=2)
    result = manager.run_debate(
        agents=sample_agents,
        query="测试问题",
        max_rounds=2,
    )

    # 初始消息 + 多轮挑战/回应
    # 第0轮: 2条初始消息
    # 第1轮: 每对 1条挑战 + 1条回应
    # 第2轮: 每对 1条挑战 + 1条回应
    assert len(result.all_messages) > 0


def test_initial_round_created(sample_agents):
    """测试第一轮初始陈述被正确记录"""
    manager = DebateManager(max_rounds=1)
    result = manager.run_debate(
        agents=sample_agents,
        query="测试问题",
        max_rounds=1,
    )

    assert len(result.rounds) >= 1
    assert result.rounds[0].round_num == 0
    assert len(result.rounds[0].initial_messages) == len(sample_agents)


def test_debate_flow_text(sample_agents):
    """测试辩论流程文本生成"""
    manager = DebateManager(max_rounds=2)
    # 先运行辩论
    manager.run_debate(agents=sample_agents, query="测试问题", max_rounds=2)
    flow_text = manager.get_debate_flow()
    assert isinstance(flow_text, str)
    assert "第" in flow_text