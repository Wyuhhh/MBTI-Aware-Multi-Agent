# MBTI-Aware Multi-Agent System

把 MBTI 16 种人格量表投射到 LLM Agent 的行为空间，让同一底座 LLM 通过不同 Prompt 模板扮演16 种"性格 Agent"，由一组性格互补的 Agent 互相辩论、投票、仲裁，输出带人格多样性的答案。

## 核心特性

- **16套MBTI性格Prompt模板**：每套包含性格描述、Few-shot锚定、性格校验问题
- **智能组合选择器**：根据任务类型自动选择合适的Agent组合
- **多轮辩论机制**：Agent之间交叉挑战，促进深度思考
- **置信度投票**：基于置信度的加权投票机制
- **多维仲裁器**：T-F/N-S/J-P冲突自动分诊处理

## 安装

```bash
pip install -r requirements.txt
```

## 快速开始

### 使用Mock客户端（无需API密钥）

```python
from mbti_multi_agent import create_system

# 创建系统
system = create_system(provider="mock")

# 解决问题
result = system.solve(
    query="我应该如何选择职业道路？",
    auto_task_detection=True,
)

print(result["consensus"])
```

### 使用OpenAI GPT

```python
from mbti_multi_agent import MBTIMultiAgentSystem
from mbti_multi_agent.llm import OpenAIClient

# 创建LLM客户端
client = OpenAIClient(api_key="your-api-key", model="gpt-4")

# 创建系统
system = MBTIMultiAgentSystem(llm_client=client)

# 解决问题
result = system.solve(
    query="是否应该为了高薪去一个不喜欢的行业？",
    task_type="ethical_dilemma",
)

print(result["consensus"])
```

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent组合选择器                            │
│  (Task Type → MBTI组合 mapping)                             │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │ Agent 1  │    │ Agent 2  │    │ Agent 3  │
        │ (e.g.,   │    │ (e.g.,   │    │ (e.g.,   │
        │  INTJ)   │    │  ENFP)   │    │  ISTJ)   │
        └──────────┘    └──────────┘    └──────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   辩论 + 投票机制                            │
│  (多轮challenge → 置信度更新 → 投票)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     多维仲裁器                               │
│  (T-F/N-S/J-P 维度冲突分诊)                                  │
└─────────────────────────────────────────────────────────────┘
```

## 16种MBTI人格类型

| 类型 | 名称 | 核心特质 |
|------|------|---------|
| INTJ | 战略家 | 逻辑驱动，擅长长远规划 |
| INTP | 逻辑学家 | 抽象分析，追求理论完备 |
| ENTJ | 指挥官 | 果断决策，驱动行动 |
| ENTP | 辩论家 | 辩证思维，挑战现状 |
| INFJ | 提倡者 | 共情洞察，关注价值 |
| INFP | 调停者 | 理想主义，忠于内心 |
| ENFJ | 主人公 | 激励人心，推动共识 |
| ENFP | 竞选者 | 热情创造，探索可能 |
| ISTJ | 检查员 | 务实可靠，遵循规则 |
| ISFJ | 守护者 | 忠诚奉献，关注细节 |
| ESTJ | 执行者 | 高效务实，维护秩序 |
| ESFJ | 提供者 | 热情助人，构建和谐 |
| ISTP | 手艺人 | 灵活务实，擅长技术 |
| ISFP | 艺术家 | 敏感审美，珍惜自由 |
| ESTP | 企业家 | 冒险实践，把握当下 |
| ESFP | 表演者 | 热情社交，享受生活 |

## Agent组合策略

| 任务类型 | Agent组合 | 适用场景 |
|---------|----------|---------|
| career_planning | INTJ + ENFP + ISTJ | 职业规划、岗位选择 |
| ethical_dilemma | INFJ + ESTP + INTP | 道德判断、价值取舍 |
| product_decision | ENTP + ISTJ + ESFJ | 产品功能、商业决策 |
| tech_solution | INTP + ISTJ + ENTJ | 技术选型、系统设计 |
| creative_ideation | ENFP + ENTP + ESFP | 头脑风暴、创意生成 |
| risk_assessment | INTJ + ISTJ + ESTP | 风险分析、预案规划 |
| team_coordination | ENFJ + ESFJ + ISTJ | 团队管理、人员协调 |
| strategic_planning | INTJ + ENTJ + INFJ | 长期规划、战略制定 |

## 仲裁维度

| 冲突维度 | 冲突双方 | 仲裁策略 |
|---------|---------|---------|
| T-F | Thinking vs Feeling | 逻辑Agent给论证链，感性Agent给共情例证，合并输出 |
| N-S | iNtuition vs Sensing | 实感派先查证据，直觉派给推演，最后整合 |
| J-P | Judging vs Perceiving | 判断派给确定性结论，感知派给开放选项，并列呈现 |

## 运行测试

```bash
pytest tests/ -v
```

## 项目结构

```
mbti-multi-agent/
├── README.md
├── requirements.txt
├── config/
│   └── agent_combinations.yaml    # 任务类型→MBTI组合映射
├── src/
│   ├── __init__.py
│   ├── main.py                    # 主入口
│   ├── mbti_prompts/
│   │   └── personalities.py       # 16套MBTI Prompt模板
│   ├── agent/
│   │   ├── base.py                # 基类MBTI Agent
│   │   ├── combinator.py          # Agent组合选择器
│   │   ├── debate.py              # 辩论机制
│   │   ├── voter.py               # 投票机制
│   │   └── arbitrator.py          # 多维仲裁器
│   └── llm/
│       └── client.py              # LLM调用封装
├── tests/
│   ├── test_personalities.py
│   ├── test_debate.py
│   └── test_arbitrator.py
└── examples/
    └── demo.py                    # 使用示例
```

## License

MIT