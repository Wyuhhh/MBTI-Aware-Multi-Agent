#!/usr/bin/env python
"""
MBTI Multi-Agent 主入口

用法:
    python run.py                          # Mock模式快速测试
    python run.py --minimax                # 使用MiniMax API
    python run.py --minimax --quick        # MiniMax快速测试(3题)
    python run.py --minimax --diagnostic   # 认知差异诊断测试
    python run.py --openai                 # 使用OpenAI API
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def run_mock_demo():
    """Mock模式快速演示"""
    print("\n" + "=" * 60)
    print("MBTI Multi-Agent System - Mock Demo")
    print("=" * 60)

    from src.main import create_system

    system = create_system(provider="mock")

    # 测试问题
    questions = [
        "我应该选择考研还是工作？",
        "发现同事在报销中作弊，应该举报吗？",
        "是否应该在APP中加入社交功能？",
    ]

    for q in questions:
        print(f"\n问题: {q}")
        print("-" * 40)

        result = system.solve(q, auto_task_detection=True)

        print(f"使用Agent: {[a['mbti_type'] for a in result['agents_info']]}")
        print(f"共识结果: {result['consensus'][:200]}...")
        print(f"置信度: {result['confidence']:.2f}")


def run_api_eval(provider: str, model: str, quick: bool = False, full: bool = False, diagnostic: bool = False):
    """API模式评估"""
    import os

    api_key = os.environ.get(f"{provider.upper()}_API_KEY")
    if not api_key and provider == "openai":
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        print("  export OPENAI_API_KEY='your-key'  (Linux/Mac)")
        return

    # MiniMax使用默认key和base_url
    if provider == "minimax":
        api_key = api_key or "sk-1234"
        base_url = os.environ.get("MINIMAX_BASE_URL", "http://10.68.46.180:31943")
        model = model or "MiniMax-M2.7"
        print(f"使用MiniMax模型: {model}")
        print(f"API地址: {base_url}")

    if quick:
        # 快速测试 3题
        print("\n" + "=" * 60)
        print(f"快速测试模式 (3题) - {provider}")
        print("=" * 60)

        from benchmark.evaluator import run_benchmark

        run_benchmark(
            provider=provider,
            api_key=api_key,
            model=model,
            debate_rounds=2,
            categories=None,
            save_report=True,
            verbose=True,
        )

    elif full:
        # 完整200题
        print("\n" + "=" * 60)
        print(f"完整评测模式 (200题) - {provider}")
        print("=" * 60)
        print("按 Ctrl+C 取消...")

        import time
        time.sleep(2)

        from benchmark.evaluator import run_benchmark

        run_benchmark(
            provider=provider,
            api_key=api_key,
            model=model,
            debate_rounds=3,
            categories=None,
            save_report=True,
            verbose=True,
        )

    elif diagnostic:
        # 认知差异诊断
        print("\n" + "=" * 60)
        print(f"认知差异诊断测试 (23题) - {provider}")
        print("=" * 60)

        from benchmark.diagnostic_tests import get_all_diagnostic_questions
        from benchmark.evaluation import run_dual_judge_evaluation

        questions = get_all_diagnostic_questions()
        print(f"加载了 {len(questions)} 道诊断测试题\n")

        run_dual_judge_evaluation(
            provider=provider,
            api_key=api_key,
            model=model,
            questions=questions,
            verbose=True,
        )

    else:
        print("请指定运行模式:")
        print("  --quick      快速测试 (3题)")
        print("  --full       完整评测 (200题)")
        print("  --diagnostic 认知差异诊断 (23题)")


def run_ablation(provider: str = "mock", model: str = None):
    """消融实验"""
    print("\n" + "=" * 60)
    print(f"Agent组合消融实验 - {provider}")
    print("=" * 60)

    from benchmark.ablation import run_ablation_experiment
    from benchmark.datasets.evaluation_200 import get_dataset

    questions = get_dataset()[:10]  # 10题做消融（减少时间）

    run_ablation_experiment(
        provider=provider,
        questions=questions,
        verbose=True,
    )


def run_statistics(provider: str = "mock"):
    """统计分析"""
    print("\n" + "=" * 60)
    print(f"统计显著性分析 - {provider}")
    print("=" * 60)

    from benchmark.statistics import run_statistical_analysis
    from benchmark.datasets.evaluation_200 import get_dataset

    questions = get_dataset()[:8]

    run_statistical_analysis(
        provider=provider,
        questions=questions,
        n_runs=3,
        verbose=True,
    )


def main():
    parser = argparse.ArgumentParser(
        description="MBTI Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                         # Mock模式演示
  python run.py --minimax --quick       # MiniMax快速测试
  python run.py --minimax --diagnostic  # MiniMax认知差异诊断
  python run.py --openai --quick        # OpenAI快速测试
  python run.py --ablation --minimax    # MiniMax消融实验
        """
    )

    parser.add_argument("--minimax", action="store_true", help="使用MiniMax API")
    parser.add_argument("--openai", action="store_true", help="使用OpenAI API")
    parser.add_argument("--quick", action="store_true", help="快速测试模式 (3题)")
    parser.add_argument("--full", action="store_true", help="完整200题评测")
    parser.add_argument("--diagnostic", action="store_true", help="认知差异诊断测试 (23题)")
    parser.add_argument("--ablation", action="store_true", help="消融实验")
    parser.add_argument("--stats", action="store_true", help="统计分析")
    parser.add_argument("--model", default=None, help="使用的模型")

    args = parser.parse_args()

    # Mock模式
    if not args.minimax and not args.openai and not any([args.ablation, args.stats]):
        run_mock_demo()
        return

    # 消融实验
    if args.ablation:
        provider = "minimax" if args.minimax else ("openai" if args.openai else "mock")
        run_ablation(provider=provider, model=args.model)
        return

    # 统计分析
    if args.stats:
        provider = "minimax" if args.minimax else ("openai" if args.openai else "mock")
        run_statistics(provider=provider)
        return

    # API模式评估
    provider = "minimax" if args.minimax else "openai"
    run_api_eval(provider=provider, model=args.model, quick=args.quick, full=args.full, diagnostic=args.diagnostic)


if __name__ == "__main__":
    main()