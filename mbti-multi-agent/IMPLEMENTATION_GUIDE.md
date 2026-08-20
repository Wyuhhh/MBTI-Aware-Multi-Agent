# MBTI Multi-Agent 实施指南

## 环境准备

```bash
cd mbti-multi-agent
pip install -r requirements.txt
```

## 运行模式

### 1. Mock模式（无需API key）

```bash
python run.py
```

输出示例：
```
MBTI Multi-Agent System - Mock Demo
问题: 我应该选择考研还是工作？
使用Agent: ['INTJ', 'ENFP', 'ISTJ']
共识结果: Mock response...
置信度: 0.50
```

### 2. 快速测试（5题，用OpenAI API）

```bash
export OPENAI_API_KEY="sk-..."
python run.py --openai --quick
```

### 3. 认知差异诊断（23题）

```bash
export OPENAI_API_KEY="sk-..."
python run.py --openai --diagnostic
```

这会验证：同质Agent vs 异质Agent 是否产生真实认知差异

### 4. 消融实验（测试Agent组合）

```bash
# 15题，测试所有Agent组合的胜率
python run.py --ablation
```

输出：
```
消融实验
基础Agent池: ['INTJ', 'ENFP', 'ISTJ', 'ENTJ', 'INFJ', 'ESTP']
测试组合数: 48
测试问题数: 15

所有组合排名:
  INTJ+ENFP+ISTJ  胜率: 71.2%  置信度: 0.68
  INTJ+ISTJ        胜率: 58.3%  置信度: 0.62
  ...
```

### 5. 完整200题评测

```bash
export OPENAI_API_KEY="sk-..."
python run.py --openai --full
```

**注意**：完整评测预计消耗 $50-100 API费用

## 各模块说明

| 模块 | 命令 | 说明 |
|-----|------|-----|
| 基线对比 | `python -m benchmark.evaluator` | 4组基线在200题上的表现 |
| 双Judge评估 | `python -m benchmark.evaluation` | 异质vs同质Agent对比 |
| 消融实验 | `python benchmark/ablation.py` | 验证最优Agent组合 |
| 统计分析 | `python benchmark/statistics.py` | 多次运行+显著性检验 |
| 诊断测试 | `python -m benchmark.diagnostic_tests` | 23道认知差异测试题 |

## 结果解读

### Krippendorff α 一致性

| α值 | 解释 |
|-----|------|
| α ≥ 0.8 | 一致性优秀 |
| 0.667 ≤ α < 0.8 | 一致性可接受 |
| α < 0.667 | 需要改进 |

### 消融实验胜率

| 组合 | 预期表现 |
|-----|---------|
| 单Agent | 基线 (~50%) |
| INTJ+ISTJ | 略好 (~58%) |
| INTJ+ENFP+ISTJ | 最好 (~70%) |
| 4+ Agents | 可能下降（冗余） |

### 统计显著性

p < 0.05 表示差异显著，可信

## 预期产出

运行后在 `benchmark/results/` 目录生成：

```
benchmark/results/
├── benchmark_report_YYYYMMDD_HHMMSS.json   # 基线对比结果
├── diagnostic_report_YYYYMMDD_HHMMSS.json  # 诊断测试结果
├── ablation_report_YYYYMMDD_HHMMSS.json    # 消融实验结果
└── stats_report_YYYYMMDD_HHMMSS.json       # 统计分析结果
```

## 核心验证目标

1. **认知差异存在性**：诊断测试题能否区分INTJ和ESFP的真实差异？
2. **组合优越性**：INTJ+ENFP+ISTJ是否确实优于其他组合？
3. **统计显著性**：多次运行结果是否稳定（p < 0.05）？

如果这三个都通过，项目假设得到验证。