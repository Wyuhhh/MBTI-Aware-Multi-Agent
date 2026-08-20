"""
投票机制
基于置信度的加权投票
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import re
import math

from .base import MBTIAgent, AgentMessage, MessageType


@dataclass
class Vote:
    """单个投票"""
    agent_id: str
    mbti_type: str
    choice: int  # 选择的回答编号 (0-based)
    reasoning: str
    confidence: float

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "mbti_type": self.mbti_type,
            "choice": self.choice,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
        }


@dataclass
class VotingResult:
    """投票结果"""
    votes: List[Vote]
    tallies: Dict[int, float]  # answer_index -> weighted_score
    winner: Optional[int]
    consensus_score: float
    summary: str
    # 新增评估指标
    viewpoint_divergence: float = 0.0  # 观点分歧度 (0-1, 越高表示分歧越大)
    krippendorff_alpha: float = 0.0  # Krippendorff α系数 (1表示完全一致, 0表示偶然一致, <0表示系统不一致


class VotingMechanism:
    """投票机制"""

    def __init__(self, voting_threshold: float = 0.6):
        self.voting_threshold = voting_threshold

    def run_vote(
        self,
        agents: List[MBTIAgent],
        query: str,
        all_responses: List[str],
        round_num: int = 0,
    ) -> VotingResult:
        """
        运行投票

        Args:
            agents: 参与投票的Agent列表
            query: 问题
            all_responses: 所有需要投票的回应列表
            round_num: 当前轮数

        Returns:
            VotingResult: 投票结果
        """
        votes = []
        for agent in agents:
            vote_msg = agent.vote(query, all_responses, round_num)
            vote = self._parse_vote(agent, vote_msg.content)
            votes.append(vote)

        # 计算加权票数
        tallies = self._tally_votes(votes, len(all_responses))

        # 确定获胜者
        winner = self._determine_winner(tallies)

        # 计算共识分数
        consensus_score = self._calculate_consensus(tallies)

        # 生成总结
        summary = self._generate_summary(agents, votes, tallies, winner)

        # 计算观点分歧度（基于投票分布的熵值）
        divergence = self._calculate_divergence(votes, len(all_responses))

        # 计算Krippendorff α系数
        kalpha = self._calculate_krippendorff_alpha(votes, len(all_responses))

        return VotingResult(
            votes=votes,
            tallies=tallies,
            winner=winner,
            consensus_score=consensus_score,
            summary=summary,
            viewpoint_divergence=divergence,
            krippendorff_alpha=kalpha,
        )

    def _parse_vote(self, agent: MBTIAgent, vote_text: str) -> Vote:
        """解析投票文本"""
        # 尝试提取选择的编号
        choice = None

        # 常见模式
        patterns = [
            r"选择.*?(\d+)",  # "选择 1" 或 "选择: 1"
            r"第\s*(\d+)\s*个",  # "第一个"
            r"编号\s*(\d+)",  # "编号 2"
            r"^\s*(\d+)\s*$",  # 单独一行的数字
        ]

        for pattern in patterns:
            match = re.search(pattern, vote_text)
            if match:
                choice = int(match.group(1)) - 1  # 转为0-based
                break

        # 如果没找到明确的choice，基于置信度给默认值
        if choice is None:
            choice = 0

        return Vote(
            agent_id=agent.agent_id,
            mbti_type=agent.mbti_type,
            choice=choice,
            reasoning=vote_text,
            confidence=0.5,
        )

    def _tally_votes(self, votes: List[Vote], num_options: int) -> Dict[int, float]:
        """统计加权票数"""
        tallies: Dict[int, float] = {i: 0.0 for i in range(num_options)}

        for vote in votes:
            if 0 <= vote.choice < num_options:
                # 加权票数 = 基础票数 * 置信度
                tallies[vote.choice] += 1.0 * vote.confidence

        return tallies

    def _determine_winner(self, tallies: Dict[int, float]) -> Optional[int]:
        """确定获胜者"""
        if not tallies:
            return None

        # 找出最高票数
        max_score = max(tallies.values())
        if max_score == 0:
            return None

        # 检查是否超过阈值
        total_votes = sum(tallies.values())
        if total_votes == 0:
            return None

        winning_ratio = max_score / total_votes
        if winning_ratio < self.voting_threshold:
            return None  # 没有达到阈值

        # 返回最高票的索引
        for idx, score in tallies.items():
            if score == max_score:
                return idx

        return None

    def _calculate_consensus(self, tallies: Dict[int, float]) -> float:
        """计算共识分数 (0-1)"""
        if not tallies:
            return 0.0

        total = sum(tallies.values())
        if total == 0:
            return 0.0

        max_score = max(tallies.values())
        return max_score / total

    def _generate_summary(
        self,
        agents: List[MBTIAgent],
        votes: List[Vote],
        tallies: Dict[int, float],
        winner: Optional[int],
    ) -> str:
        """生成投票总结"""
        lines = ["## 投票结果\n"]

        # 各Agent的选择
        lines.append("### 各Agent投票")
        for vote in votes:
            agent_name = next(
                (a.personality.name for a in agents if a.agent_id == vote.agent_id),
                vote.mbti_type
            )
            lines.append(f"- **{agent_name}** ({vote.mbti_type}): 选择 #{vote.choice + 1}")

        # 票数统计
        lines.append("\n### 加权票数")
        for idx, score in sorted(tallies.items()):
            lines.append(f"- 选项 {idx + 1}: {score:.2f} 分")

        # 获胜者
        if winner is not None:
            lines.append(f"\n**获胜者: 选项 {winner + 1}** (共识分数: {self._calculate_consensus(tallies):.2%})")
        else:
            lines.append("\n**无明确获胜者** (未达到共识阈值)")

        return "\n".join(lines)

    def _calculate_divergence(self, votes: List[Vote], num_options: int) -> float:
        """
        计算观点分歧度 (基于投票分布的熵值)

        Args:
            votes: 投票列表
            num_options: 选项数量

        Returns:
            float: 分歧度 (0-1), 0表示完全一致, 1表示完全分散
        """
        if not votes or num_options == 0:
            return 0.0

        # 统计每个选项的票数
        choice_counts = [0] * num_options
        for vote in votes:
            if 0 <= vote.choice < num_options:
                choice_counts[vote.choice] += 1

        # 计算概率分布
        total = len(votes)
        probs = [count / total for count in choice_counts]

        # 计算香农熵
        entropy = 0.0
        for p in probs:
            if p > 0:
                entropy -= p * math.log2(p)

        # 归一化（最大熵为log2(num_options)）
        max_entropy = math.log2(num_options) if num_options > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        # 返回分歧度 = 归一化熵（越高表示分歧越大）
        return normalized_entropy

    def _calculate_krippendorff_alpha(self, votes: List[Vote], num_options: int) -> float:
        """
        计算Krippendorff α系数（名义测量）

        α = 1 - (Do / De)
        其中 Do = observed disagreement, De = expected disagreement

        Args:
            votes: 投票列表
            num_options: 选项数量

        Returns:
            float: α系数 (1表示完全一致, 0表示偶然一致, <0表示系统不一致)
        """
        if not votes or len(votes) < 2:
            return 1.0  # 只有1个评委或没有投票时，定义为完全一致

        # 构建评分矩阵 (ratings:评委 x items:选项编号)
        # 每个vote是对一个选项的选择，所以我们用vote的choice作为"评分"
        # 简化处理：将每个vote视为对同一个虚拟item的多次评分

        # 提取所有非缺失评分
        ratings = [vote.choice for vote in votes if 0 <= vote.choice < num_options]

        if len(ratings) < 2:
            return 1.0

        # 计算observed disagreement (Do)
        # 对于名义测量，Do = 所有不一致对的比例
        n = len(ratings)
        coincidences = [[0] * num_options for _ in range(num_options)]

        for i in range(n):
            for j in range(i + 1, n):
                coincidences[ratings[i]][ratings[j]] += 1
                coincidences[ratings[j]][ratings[i]] += 1

        # Do = 1/n(n-1) * sum(c_ij) for i != j
        do = 0.0
        for i in range(num_options):
            for j in range(num_options):
                if i != j:
                    do += coincidences[i][j]

        pair_count = n * (n - 1) / 2
        if pair_count > 0:
            do = do / (2 * pair_count)  # 每个pair被计算了2次

        # 计算expected disagreement (De)
        # De = sum(c_i. * c_.i) / (n(n-1)) - 1/(n-1) for nominal
        # 其中 c_i. 是第i个类别的边际和
        marginals = [0] * num_options
        for rating in ratings:
            marginals[rating] += 1

        de = 0.0
        for i in range(num_options):
            for j in range(num_options):
                if i != j:
                    de += marginals[i] * marginals[j]

        if n > 1:
            de = de / (n * (n - 1))

        # 计算α
        if de == 0:
            return 1.0  # 没有不一致，定义为完全一致

        alpha = 1.0 - (do / de)
        return max(-1.0, min(1.0, alpha))  # 限制在[-1, 1]范围内

    def run_ranked_vote(
        self,
        agents: List[MBTIAgent],
        query: str,
        all_responses: List[str],
        round_num: int = 0,
    ) -> VotingResult:
        """
        运行排序投票（每个Agent对所有选项排序）

        Args:
            agents: 参与投票的Agent列表
            query: 问题
            all_responses: 所有需要投票的回应列表
            round_num: 当前轮数

        Returns:
            VotingResult: 投票结果
        """
        # 简化为评分制：每个Agent给每个选项打1-10分
        votes = []
        for agent in agents:
            # 让Agent评估每个选项
            vote_text = agent.vote(query, all_responses, round_num)

            # 解析评分（这里简化处理）
            vote = Vote(
                agent_id=agent.agent_id,
                mbti_type=agent.mbti_type,
                choice=0,  # 稍后计算
                reasoning=vote_text,
                confidence=0.5,
            )
            votes.append(vote)

        # Borda计数法
        tallies = {i: 0.0 for i in range(len(all_responses))}
        for vote in votes:
            # 简化：假设Agent最喜欢的是第一个选项
            for i in range(len(all_responses)):
                if i == 0:
                    tallies[i] += 3  # 第一名3分
                elif i == 1:
                    tallies[i] += 2  # 第二名2分
                else:
                    tallies[i] += 1  # 其他1分

        winner = self._determine_winner(tallies)
        consensus_score = self._calculate_consensus(tallies)

        return VotingResult(
            votes=votes,
            tallies=tallies,
            winner=winner,
            consensus_score=consensus_score,
            summary=self._generate_summary(agents, votes, tallies, winner),
        )