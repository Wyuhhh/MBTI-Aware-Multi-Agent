# MBTI-Aware Multi-Agent System

把 MBTI 16 种人格量表投射到 LLM Agent 的行为空间，让同一底座 LLM 通过不同 Prompt 模板扮演16 种"性格 Agent"，由一组性格互补的 Agent 互相辩论、投票、仲裁，输出带人格多样性的答案。

## 核心创新

> **同质 Agent 的群智 ≠ 真群智** —— 3 个一样的 GPT-4 互相 challenge，本质还是 GPT-4
>
> **异质 Agent 才能产生认知冲突** —— INTJ（战略）+ ESFP（共情）+ ISTJ（务实）三个角色天然存在视角差异

## 快速开始

```bash
# Mock模式演示（无需API key）
python run.py

# OpenAI快速测试
export OPENAI_API_KEY="sk-..."
python run.py --openai --quick
```

## 项目结构

```
mbti-multi-agent/
├── run.py                      # 主入口
├── src/
│   ├── main.py                 # MBTIMultiAgentSystem
│   ├── mbti_prompts/
│   │   ├── personalities.py    # 16套MBTI Prompt
│   │   └── personalities_v2.py # 知识约束版
│   ├── agent/
│   │   ├── base.py             # MBTI Agent
│   │   ├── combinator.py       # Agent组合选择器
│   │   ├── debate.py           # 辩论机制
│   │   ├── voter.py            # 投票机制
│   │   └── arbitrator.py       # 多维仲裁器
│   └── llm/client.py           # LLM客户端
├── benchmark/
│   ├── evaluator.py            # 基线对比（4组基线x200题）
│   ├── evaluation.py           # 双Judge评估 + Krippendorff α
│   ├── ablation.py             # 消融实验（Agent组合）
│   ├── statistics.py           # 统计分析（多次运行）
│   ├── diagnostic_tests.py     # 23道认知差异诊断题
│   └── datasets/evaluation_200.py  # 200题评测集
├── tests/                      # 单元测试
└── IMPLEMENTATION_GUIDE.md     # 实施指南
```

## 核心模块

### 1. 16套MBTI Prompt模板

每套包含：
- 性格描述（MBTI维度的语言化定义）
- Few-shot锚定（3-5个示范问答）
- 知识约束（专业领域 vs 不熟悉领域）
- 性格校验问题（5个反问确保不"演过头"）

### 2. Agent组合选择器

| 任务类型 | Agent组合 | 理由 |
|---------|----------|------|
| 职业规划 | INTJ + ENFP + ISTJ | 战略+创造+务实 |
| 伦理困境 | INFJ + ESTP + INTP | 共情+行动+分析 |
| 产品决策 | ENTP + ISTJ + ESFJ | 辩证+可靠+用户视角 |

### 3. 辩论机制

```
初始陈述 → 交叉挑战 → 置信度更新 → 多轮迭代 → 最终投票
```

### 4. 多维仲裁器

| 冲突维度 | 仲裁策略 |
|---------|---------|
| T-F | 逻辑Agent给论证链，感性Agent给共情例证 |
| N-S | 实感派先查证据，直觉派给推演 |
| J-P | 判断派给确定性结论，感知派给开放选项 |

## 评测体系

### 4组基线

| 基线 | 说明 |
|-----|------|
| homogeneous_INTJ | 同质Agent (3x INTJ) |
| random_mbti | 随机MBTI组合 |
| single_INTJ | 单Agent基线 |
| oracle | 异质组合 (INTJ+ENFP+ISTJ) |

### 评估指标

- **双Judge评估**：质量Judge(0-4分) + 比较Judge(胜负判断)
- **Krippendorff α**：评分一致性检验
- **McNemar检验**：统计显著性
- **消融实验**：Agent贡献度分析

## 技术栈

- Python 3.10+
- OpenAI API / Anthropic API
- NumPy + SciPy (统计分析)
- PyYAML (配置)
- Pytest (测试)

## 关键挑战与解决

| 挑战 | 解决方案 |
|-----|---------|
| 本质同质性 | 知识约束创造真实认知差异 |
| Prompt vs 认知 | 23道诊断测试题验证 |
| 组合策略 | 消融实验验证最优组合 |
| 可复现性 | 多次运行 + 置信区间 |

详见 [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)