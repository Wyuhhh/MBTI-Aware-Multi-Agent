"""
MBTI Multi-Agent System 使用示例
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import MBTIMultiAgentSystem, create_system
from src.llm.client import MockLLMClient, OpenAIClient

# ============================================================
# 示例1: 使用Mock客户端（无需API密钥）
# ============================================================

print("=" * 60)
print("示例1: 使用Mock客户端")
print("=" * 60)

# 创建Mock系统
mock_system = create_system(provider="mock")

# 定义问题
query = "我应该如何选择职业道路？"

# 使用自动任务检测
result = mock_system.solve(
    query=query,
    auto_task_detection=True,
)

print(f"\n问题: {query}")
print(f"\n检测到的Agent组合:")
for agent_info in result["agents_info"]:
    print(f"  - {agent_info['mbti_type']} ({agent_info['name']})")

print(f"\n共识结果:\n{result['consensus'][:500]}...")
print(f"\n置信度: {result['confidence']:.2f}")

# ============================================================
# 示例2: 使用自定义Agent组合
# ============================================================

print("\n" + "=" * 60)
print("示例2: 使用自定义Agent组合")
print("=" * 60)

# 创建系统
system = MBTIMultiAgentSystem(llm_client=MockLLMClient())

# 设置自定义Agent组合
system.set_agents(["INTJ", "ESTP", "INFJ"])

# 解决问题
result = system.solve(
    query="是否应该为了高薪去一个不喜欢的行业？",
    agent_types=["INTJ", "ESTP", "INFJ"],
    rounds=2,
)

print(f"\n问题: 是否应该为了高薪去一个不喜欢的行业？")
print(f"\n参与Agent:")
for agent_info in result["agents_info"]:
    print(f"  - {agent_info['mbti_type']} ({agent_info['name']})")
    print(f"    特质: {', '.join(agent_info['core_traits'][:3])}")

print(f"\n维度分析:")
for dim, analysis in result["dimension_analysis"].items():
    print(f"  {dim}: {analysis}")

print(f"\n完整总结:\n{result['full_summary']}")

# ============================================================
# 示例3: 伦理困境场景
# ============================================================

print("\n" + "=" * 60)
print("示例3: 伦理困境场景")
print("=" * 60)

system = MBTIMultiAgentSystem(llm_client=MockLLMClient())

result = system.solve(
    query="公司发现员工在报销中有小額欺诈，但这位员工工作表现很好。应该如何处理？",
    task_type="ethical_dilemma",
)

print(f"\n问题: {query}")
print(f"\n使用Agent组合: {[a['mbti_type'] for a in result['agents_info']]}")
print(f"\n替代选项:")
for i, alt in enumerate(result['alternatives'], 1):
    print(f"  {i}. {alt[:200]}...")

# ============================================================
# 示例4: 产品决策场景
# ============================================================

print("\n" + "=" * 60)
print("示例4: 产品决策场景")
print("=" * 60)

system = MBTIMultiAgentSystem(llm_client=MockLLMClient())

result = system.solve(
    query="是否应该在APP中加入社交功能来增加用户粘性？",
    task_type="product_decision",
)

print(f"\n问题: {result['query'] if 'query' in result else '是否应该在APP中加入社交功能来增加用户粘性？'}")
print(f"\n使用Agent组合: {[a['mbti_type'] for a in result['agents_info']]}")
print(f"\n投票结果:\n{result['voting_result']}")

# ============================================================
# 示例5: 列出所有可用的任务类型
# ============================================================

print("\n" + "=" * 60)
print("示例5: 可用的任务类型")
print("=" * 60)

system = MBTIMultiAgentSystem(llm_client=MockLLMClient())
task_types = system.get_available_task_types()

print("\n可用的任务类型:")
for task_type in task_types:
    print(f"  - {task_type}")

# ============================================================
# 示例6: 注册自定义Agent组合
# ============================================================

print("\n" + "=" * 60)
print("示例6: 注册自定义Agent组合")
print("=" * 60)

system = MBTIMultiAgentSystem(llm_client=MockLLMClient())

# 注册新组合
system.register_custom_combination(
    name="legal_analysis",
    agents=["INTJ", "ISTJ", "ENFJ"],
    rounds=4,
    voting_threshold=0.7,
    description="法律分析专用组合",
)

# 使用自定义组合
result = system.solve(
    query="这份合同有哪些潜在风险？",
    task_type="legal_analysis",
)

print(f"\n问题: 这份合同有哪些潜在风险？")
print(f"\n使用Agent组合: {[a['mbti_type'] for a in result['agents_info']]}")

print("\n" + "=" * 60)
print("演示完成！")
print("=" * 60)
print("""
要使用真实的LLM，请替换MockLLMClient为OpenAIClient或AnthropicClient：

from src.llm.client import OpenAIClient
client = OpenAIClient(api_key="your-api-key", model="gpt-4")
system = MBTIMultiAgentSystem(llm_client=client)
""")