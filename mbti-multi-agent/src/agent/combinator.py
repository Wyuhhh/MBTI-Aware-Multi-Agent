"""
Agent组合选择器
根据任务类型选择合适的MBTI Agent组合
"""

import yaml
from pathlib import Path
from typing import List, Dict, Optional

from dataclasses import dataclass

from .base import MBTIAgent
from ..llm.client import LLMClient


@dataclass
class AgentCombination:
    """Agent组合配置"""
    name: str
    agents: List[str]
    rounds: int
    voting_threshold: float
    description: str


class AgentCombinator:
    """Agent组合选择器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化组合选择器

        Args:
            config_path: 配置文件路径，默认使用项目内置配置
        """
        self.config_path = config_path
        self.task_combinations: Dict[str, Dict] = {}
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        if self.config_path:
            config_file = Path(self.config_path)
        else:
            # 默认配置
            config_file = Path(__file__).parent.parent.parent / "config" / "agent_combinations.yaml"

        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.task_combinations = config.get("task_combinations", {})
        else:
            # 内置默认配置
            self.task_combinations = {
                "career_planning": {
                    "agents": ["INTJ", "ENFP", "ISTJ"],
                    "rounds": 3,
                    "voting_threshold": 0.6,
                    "description": "适合职业发展、岗位选择等规划类问题",
                },
                "ethical_dilemma": {
                    "agents": ["INFJ", "ESTP", "INTP"],
                    "rounds": 4,
                    "voting_threshold": 0.5,
                    "description": "适合道德判断、价值取舍等伦理问题",
                },
                "product_decision": {
                    "agents": ["ENTP", "ISTJ", "ESFJ"],
                    "rounds": 3,
                    "voting_threshold": 0.6,
                    "description": "适合产品功能、商业决策等问题",
                },
                "tech_solution": {
                    "agents": ["INTP", "ISTJ", "ENTJ"],
                    "rounds": 3,
                    "voting_threshold": 0.7,
                    "description": "适合技术选型、系统设计等问题",
                },
                "creative_ideation": {
                    "agents": ["ENFP", "ENTP", "ESFP"],
                    "rounds": 2,
                    "voting_threshold": 0.5,
                    "description": "适合头脑风暴、创意生成等问题",
                },
                "risk_assessment": {
                    "agents": ["INTJ", "ISTJ", "ESTP"],
                    "rounds": 4,
                    "voting_threshold": 0.7,
                    "description": "适合风险分析、预案规划等问题",
                },
                "team_coordination": {
                    "agents": ["ENFJ", "ESFJ", "ISTJ"],
                    "rounds": 3,
                    "voting_threshold": 0.6,
                    "description": "适合团队管理、人员协调等问题",
                },
                "strategic_planning": {
                    "agents": ["INTJ", "ENTJ", "INFJ"],
                    "rounds": 4,
                    "voting_threshold": 0.65,
                    "description": "适合长期规划、战略制定等问题",
                },
            }

    def get_combination(self, task_type: str) -> AgentCombination:
        """
        获取指定任务类型的Agent组合

        Args:
            task_type: 任务类型 (如 "career_planning", "ethical_dilemma" 等)

        Returns:
            AgentCombination: Agent组合配置

        Raises:
            ValueError: 未知的任务类型
        """
        if task_type not in self.task_combinations:
            # 尝试模糊匹配
            for key in self.task_combinations:
                if task_type.lower() in key.lower():
                    task_type = key
                    break
            else:
                # 返回默认组合
                default_cfg = self.task_combinations.get("default", {
                    "agents": ["INTJ", "ENFP", "ISTJ"],
                    "rounds": 3,
                    "voting_threshold": 0.6,
                    "description": "默认组合",
                })
                return AgentCombination(
                    name="default",
                    agents=default_cfg.get("agents", ["INTJ", "ENFP", "ISTJ"]),
                    rounds=default_cfg.get("rounds", 3),
                    voting_threshold=default_cfg.get("voting_threshold", 0.6),
                    description=default_cfg.get("description", "默认组合"),
                )

        cfg = self.task_combinations[task_type]
        return AgentCombination(
            name=task_type,
            agents=cfg["agents"],
            rounds=cfg.get("rounds", 3),
            voting_threshold=cfg.get("voting_threshold", 0.6),
            description=cfg.get("description", ""),
        )

    def create_agents(
        self, task_type: str, llm_client: LLMClient
    ) -> List[MBTIAgent]:
        """
        根据任务类型创建Agent组合

        Args:
            task_type: 任务类型
            llm_client: LLM客户端

        Returns:
            List[MBTIAgent]: 创建的Agent列表
        """
        combination = self.get_combination(task_type)
        agents = []

        for i, mbti_type in enumerate(combination.agents):
            agent = MBTIAgent(
                mbti_type=mbti_type,
                llm_client=llm_client,
                agent_id=f"{task_type}_{mbti_type}_{i}",
            )
            agents.append(agent)

        return agents

    def get_available_task_types(self) -> List[str]:
        """获取所有可用的任务类型"""
        return list(self.task_combinations.keys())

    def register_combination(self, name: str, agents: List[str], rounds: int = 3, voting_threshold: float = 0.6, description: str = ""):
        """
        注册新的Agent组合

        Args:
            name: 组合名称
            agents: MBTI类型列表
            rounds: 辩论轮数
            voting_threshold: 投票阈值
            description: 组合描述
        """
        self.task_combinations[name] = {
            "agents": agents,
            "rounds": rounds,
            "voting_threshold": voting_threshold,
            "description": description,
        }

    def analyze_task(self, query: str) -> str:
        """
        根据查询内容分析推荐的任务类型

        Args:
            query: 用户查询

        Returns:
            str: 推荐的任务类型
        """
        query_lower = query.lower()

        # 关键词匹配
        if any(kw in query_lower for kw in ["职业", "工作", "岗位", "发展", "规划"]):
            return "career_planning"
        elif any(kw in query_lower for kw in ["道德", "伦理", "对错", "应该", "价值"]):
            return "ethical_dilemma"
        elif any(kw in query_lower for kw in ["产品", "功能", "决策", "商业", "用户"]):
            return "product_decision"
        elif any(kw in query_lower for kw in ["技术", "架构", "方案", "设计", "系统"]):
            return "tech_solution"
        elif any(kw in query_lower for kw in ["创意", "头脑风暴", "想法", "创新"]):
            return "creative_ideation"
        elif any(kw in query_lower for kw in ["风险", "预防", "预案", "危险"]):
            return "risk_assessment"
        elif any(kw in query_lower for kw in ["团队", "协调", "管理", "合作"]):
            return "team_coordination"
        elif any(kw in query_lower for kw in ["战略", "长期", "规划", "方向"]):
            return "strategic_planning"
        else:
            return "default"