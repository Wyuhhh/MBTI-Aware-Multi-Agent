#!/bin/bash
# ============================================================
# MBTI Multi-Agent Benchmark 一键复现脚本
# ============================================================
# 使用方法:
#   Unix/Linux/Mac: ./reproduce.sh
#   Windows:       bash reproduce.sh
# ============================================================

set -e  # 遇到错误立即退出

echo "============================================================"
echo "MBTI Multi-Agent Benchmark 一键复现"
echo "============================================================"
echo ""

# 配置
PROVIDER="${PROVIDER:-mock}"           # mock, openai, anthropic
MODEL="${MODEL:-gpt-4}"                # gpt-4, gpt-3.5-turbo, claude-3-5-sonnet
API_KEY="${API_KEY:-}"                 # 如果使用真实API
DEBATE_ROUNDS="${DEBATE_ROUNDS:-2}"    # 辩论轮数
CATEGORIES="${CATEGORIES:-}"           # 空表示全部类别，空格分隔

# 检查Python
echo "检查环境..."
command -v python >/dev/null 2>&1 || { echo "Error: Python未安装"; exit 1; }
echo "  Python: $(python --version)"
echo ""

# 安装依赖
echo "安装依赖..."
pip install -q pyyaml
echo "  依赖安装完成"
echo ""

# 创建结果目录
mkdir -p benchmark/results

# 构建命令
CMD="python -m benchmark.evaluator"
CMD="$CMD --provider $PROVIDER"
CMD="$CMD --model $MODEL"
CMD="$CMD --rounds $DEBATE_ROUNDS"

if [ -n "$API_KEY" ]; then
    CMD="$CMD --api-key $API_KEY"
fi

if [ -n "$CATEGORIES" ]; then
    CMD="$CMD --categories $CATEGORIES"
fi

echo "============================================================"
echo "运行配置:"
echo "  Provider: $PROVIDER"
echo "  Model: $MODEL"
echo "  Debate Rounds: $DEBATE_ROUNDS"
if [ -n "$CATEGORIES" ]; then
    echo "  Categories: $CATEGORIES"
else
    echo "  Categories: ALL"
fi
echo "============================================================"
echo ""

# 运行评测
echo "开始评测..."
echo ""
$CMD

echo ""
echo "============================================================"
echo "评测完成!"
echo "结果保存在: benchmark/results/"
echo "============================================================"