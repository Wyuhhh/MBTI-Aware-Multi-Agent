# MBTI Multi-Agent Benchmark

## 概述

完整的评测体系，包含：
- **200题评测集**：覆盖8个领域的标准化问题
- **4组基线**：同质Agent、随机MBTI、单Agent、Oracle
- **双Judge评估**：质量Judge + 比较Judge
- **Krippendorff α一致性**：评估评分者间一致性

## 快速开始

### 一键运行评测

```bash
# Mock模式（无需API key）
bash benchmark/reproduce.sh

# 或直接运行
python -m benchmark.evaluator --provider mock --rounds 2
```

### 双Judge评估

```bash
# 运行双Judge评估
python -m benchmark.evaluation --provider mock --limit 10

# 完整200题评估（需要真实API）
python -m benchmark.evaluation --provider openai --api-key $OPENAI_API_KEY
```

## 评测模块

### benchmark/evaluator.py - 基线对比

对比4组基线在不同问题上的表现：

| 基线 | 说明 |
|-----|------|
| `homogeneous_INTJ` | 3个同质INTJ Agent |
| `random_mbti` | 随机3个MBTI组合 |
| `single_INTJ` | 单Agent INTJ |
| `oracle` | 异质组合INTJ+ENFP+ISTJ |

### benchmark/evaluation.py - 双Judge评估

**Judge1 (异质)**: Oracle (INTJ+ENFP+ISTJ)
**Judge2 (同质)**: Homogeneous (3x INTJ)

评估流程：
1. 两个Judge对同一问题生成回答
2. QualityJudge评估每个回答的质量(0-4分)
3. ComparativeJudge判断哪个回答更好
4. 计算Krippendorff α一致性

**Krippendorff α 解读**:
- α ≥ 0.8: 一致性优秀
- 0.667 ≤ α < 0.8: 一致性可接受
- 0.5 ≤ α < 0.667: 一致性一般
- α < 0.5: 一致性差，需改进

## 输出结果

结果保存在 `benchmark/results/`，包含：
- JSON格式详细报告
- 各基线对比数据
- Krippendorff α计算结果
- 统计显著性检验结果

## 项目结构

```
benchmark/
├── baselines/
│   └── core.py              # 4组基线实现
├── datasets/
│   └── evaluation_200.py    # 200题评测集
├── evaluator.py             # 基线对比评测
├── evaluation.py            # 双Judge评估
├── reproduce.sh             # 一键复现脚本
├── reproduce.bat            # Windows版
└── results/                 # 评测结果
```