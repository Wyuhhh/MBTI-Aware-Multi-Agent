#!/bin/bash
# MBTI Multi-Agent 评测一键复现脚本

echo "=========================================="
echo "MBTI Multi-Agent Benchmark 一键复现"
echo "=========================================="
echo ""

# 检查依赖
echo "检查依赖..."
python -c "import numpy, scipy" 2>/dev/null || {
    echo "安装依赖..."
    pip install numpy scipy -q
}
echo "依赖检查完成"
echo ""

# 1. 快速基线测试 (3题)
echo "=========================================="
echo "Step 1: 基线对比测试 (3题)"
echo "=========================================="
python -m benchmark.evaluator --provider mock --limit 3 --rounds 2 --quiet
echo ""

# 2. 双Judge评估 (3题)
echo "=========================================="
echo "Step 2: 双Judge评估 (3题)"
echo "=========================================="
python -m benchmark.evaluation --provider mock --limit 3
echo ""

# 3. 消融实验 (简化版，10题)
echo "=========================================="
echo "Step 3: 消融实验 (10题)"
echo "=========================================="
python benchmark/ablation.py --provider mock --limit 10
echo ""

# 4. 统计分析 (3题 x 2次运行)
echo "=========================================="
echo "Step 4: 统计分析 (3题 x 2次运行)"
echo "=========================================="
python benchmark/statistics.py --provider mock --limit 3 --runs 2
echo ""

echo "=========================================="
echo "所有测试完成！"
echo "=========================================="
echo ""
echo "详细结果请查看:"
echo "  - benchmark/results/           (基线对比结果)"
echo "  - benchmark/diagnostic_tests.py (诊断测试题)"
echo ""
echo "使用真实API运行完整评测:"
echo "  export OPENAI_API_KEY='your-key'"
echo "  python -m benchmark.evaluator --provider openai --model gpt-4"
echo "  python -m benchmark.evaluation --provider openai --model gpt-4"