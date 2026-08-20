"""
MBTI Multi-Agent System 主入口
"""

from typing import Optional, List, Dict, Any

from .llm.client import LLMClient, OpenAIClient, AnthropicClient, MockLLMClient, MiniMaxClient
from .agent.base import MBTIAgent, AgentMessage
from .agent.combinator import AgentCombinator, AgentCombination
from .agent.debate import DebateManager, DebateResult
from .agent.voter import VotingMechanism, VotingResult
from .agent.arbitrator import MultiDimensionArbitrator, ArbitrationResult


class MBTIMultiAgentSystem:
    """
    MBTI多智能体系统

    使用方法:
    >>> from mbti_multi_agent import MBTIMultiAgentSystem, OpenAIClient
    >>> client = OpenAIClient(model="gpt-4")
    >>> system = MBTIMultiAgentSystem(llm_client=client)
    >>> result = system.solve("我应该如何选择职业？", task_type="career_planning")
    """

    def __init__(
        self,
        llm_client: LLMClient,
        config_path: Optional[str] = None,
        default_rounds: int = 3,
        default_voting_threshold: float = 0.6,
    ):
        """
        初始化系统

        Args:
            llm_client: LLM客户端
            config_path: Agent组合配置文件路径
            default_rounds: 默认辩论轮数
            default_voting_threshold: 默认投票阈值
        """
        self.llm_client = llm_client
        self.combinator = AgentCombinator(config_path)
        self.debate_manager = DebateManager(max_rounds=default_rounds)
        self.voting_mechanism = VotingMechanism(voting_threshold=default_voting_threshold)
        self.arbitrator = MultiDimensionArbitrator(llm_client)

        self.agents: List[MBTIAgent] = []
        self.current_debate_result: Optional[DebateResult] = None
        self.current_voting_result: Optional[VotingResult] = None
        self.current_arbitration_result: Optional[ArbitrationResult] = None

    def solve(
        self,
        query: str,
        task_type: Optional[str] = None,
        agent_types: Optional[List[str]] = None,
        rounds: Optional[int] = None,
        auto_task_detection: bool = True,
    ) -> Dict[str, Any]:
        """
        解决用户查询

        Args:
            query: 用户问题
            task_type: 任务类型（如 "career_planning", "ethical_dilemma" 等）
            agent_types: 直接指定Agent类型列表（覆盖task_type）
            rounds: 辩论轮数
            auto_task_detection: 是否自动检测任务类型

        Returns:
            Dict containing:
                - consensus: 仲裁后的共识
                - alternatives: 替代选项
                - reasoning_chain: 逻辑论证链
                - empathy_examples: 共情例证
                - dimension_analysis: 维度分析
                - agents_info: Agent信息
                - confidence: 置信度
        """
        # 确定任务类型和Agent组合
        if agent_types:
            combination = AgentCombination(
                name="custom",
                agents=agent_types,
                rounds=rounds or self.debate_manager.max_rounds,
                voting_threshold=self.voting_mechanism.voting_threshold,
                description="自定义组合",
            )
        elif task_type:
            combination = self.combinator.get_combination(task_type)
        elif auto_task_detection:
            detected_type = self.combinator.analyze_task(query)
            combination = self.combinator.get_combination(detected_type)
        else:
            combination = self.combinator.get_combination("default")

        # 创建Agents
        self.agents = []
        for i, mbti_type in enumerate(combination.agents):
            agent = MBTIAgent(
                mbti_type=mbti_type,
                llm_client=self.llm_client,
                agent_id=f"{combination.name}_{mbti_type}_{i}",
            )
            self.agents.append(agent)

        # 运行辩论
        actual_rounds = rounds or combination.rounds
        self.current_debate_result = self.debate_manager.run_debate(
            agents=self.agents,
            query=query,
            max_rounds=actual_rounds,
        )

        # 运行投票
        final_responses = list(self.current_debate_result.final_positions.values())
        self.current_voting_result = self.voting_mechanism.run_vote(
            agents=self.agents,
            query=query,
            all_responses=final_responses,
            round_num=actual_rounds + 1,
        )

        # 仲裁
        self.current_arbitration_result = self.arbitrator.arbitrate(
            agents=self.agents,
            messages=self.current_debate_result.all_messages,
            query=query,
        )

        return {
            "consensus": self.current_arbitration_result.consensus,
            "alternatives": self.current_arbitration_result.alternatives,
            "reasoning_chain": self.current_arbitration_result.reasoning_chain,
            "empathy_examples": self.current_arbitration_result.empathy_examples,
            "dimension_analysis": self.current_arbitration_result.dimension_analysis,
            "agents_info": self._get_agents_info(),
            "confidence": self.current_arbitration_result.confidence,
            "voting_result": self.current_voting_result.summary,
            "full_summary": self.current_arbitration_result.final_summary,
        }

    def _get_agents_info(self) -> List[Dict[str, str]]:
        """获取当前Agent信息"""
        return [
            {
                "id": agent.agent_id,
                "mbti_type": agent.mbti_type,
                "name": agent.personality.name,
                "core_traits": agent.personality.core_traits,
            }
            for agent in self.agents
        ]

    def add_agent(self, mbti_type: str) -> MBTIAgent:
        """添加指定类型的Agent"""
        agent = MBTIAgent(
            mbti_type=mbti_type,
            llm_client=self.llm_client,
            agent_id=f"{mbti_type}_{len(self.agents)}",
        )
        self.agents.append(agent)
        return agent

    def set_agents(self, mbti_types: List[str]) -> List[MBTIAgent]:
        """设置Agent组合"""
        self.agents = []
        for i, mbti_type in enumerate(mbti_types):
            agent = MBTIAgent(
                mbti_type=mbti_type,
                llm_client=self.llm_client,
                agent_id=f"{mbti_type}_{i}",
            )
            self.agents.append(agent)
        return self.agents

    def get_available_task_types(self) -> List[str]:
        """获取所有可用的任务类型"""
        return self.combinator.get_available_task_types()

    def register_custom_combination(
        self,
        name: str,
        agents: List[str],
        rounds: int = 3,
        voting_threshold: float = 0.6,
        description: str = "",
    ):
        """注册自定义Agent组合"""
        self.combinator.register_combination(
            name=name,
            agents=agents,
            rounds=rounds,
            voting_threshold=voting_threshold,
            description=description,
        )

    def reset(self):
        """重置系统状态"""
        for agent in self.agents:
            agent.reset()
        self.agents = []
        self.current_debate_result = None
        self.current_voting_result = None
        self.current_arbitration_result = None


def create_system(
    provider: str = "openai",
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    **kwargs,
) -> MBTIMultiAgentSystem:
    """
    工厂函数：创建系统实例

    Args:
        provider: LLM提供商 ("openai", "anthropic", "minimax", "mock")
        model: 模型名称
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        MBTIMultiAgentSystem实例
    """
    if provider == "openai":
        llm_client = OpenAIClient(api_key=api_key, model=model, **kwargs)
    elif provider == "anthropic":
        llm_client = AnthropicClient(api_key=api_key, model=model, **kwargs)
    elif provider == "minimax":
        llm_client = MiniMaxClient(api_key=api_key, model=model, **kwargs)
    elif provider == "mock":
        llm_client = MockLLMClient(**kwargs)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    return MBTIMultiAgentSystem(llm_client=llm_client)