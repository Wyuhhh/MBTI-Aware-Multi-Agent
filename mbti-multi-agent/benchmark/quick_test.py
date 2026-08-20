"""
快速测试脚本 - 只跑5题验证流程
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.evaluator import BenchmarkEvaluator
from benchmark.datasets.evaluation_200 import get_dataset
from src.llm.client import MockLLMClient

# 使用Mock客户端快速测试
llm_client = MockLLMClient()
evaluator = BenchmarkEvaluator(llm_client=llm_client, debate_rounds=2)

# 只取前5题
dataset = get_dataset()[:5]

print("快速测试 - 只评测5题")
print("=" * 60)

report = evaluator.run_full_benchmark(dataset=dataset, verbose=True)
evaluator.print_summary(report)
evaluator.save_report(report)