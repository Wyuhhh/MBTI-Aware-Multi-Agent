# MBTI Multi-Agent Web Application

MBTI人格多智能体辩论系统的完整Web前后端应用。

## 核心思想

**同质Agent的群智 ≠ 真群智** — 3个一样的GPT-4互相challenge，本质还是GPT-4的单一视角自我强化。

**异质Agent才能产生认知冲突** — 本系统通过"知识约束"机制（而非简单的人格描述）为不同MBTI Agent注入差异化知识：
- INTJ Agent 被强制注入战略博弈知识
- ESFP Agent 被强制注入用户共情知识
- ISTJ Agent 被强制注入规范执行知识

使Agent在同一问题上天然存在**信息不对称**，产生真实的认知冲突与视角差异。

## 核心创新

1. **知识约束机制**：通过为不同人格Agent注入差异化知识（战略博弈/用户共情/技术细节等），而非仅依赖人格描述，产生真实认知差异
2. **智能组合选择器**：根据任务类型（职业规划/伦理困境/技术方案等）自动选择最优Agent组合策略，标注认知维度冲突
3. **多维辩论机制**：初始陈述 → 交叉挑战 → 置信度更新 → 投票，T-F/N-S/J-P冲突自动分诊处理
4. **DualJudge评估体系**：QualityJudge（质量评判）+ ComparativeJudge（对比评判）+ Krippendorff α系数（评委一致性）

## 快速开始

### 方式1: Docker部署（推荐）

```bash
cd mbti-multi-agent-web

# 设置API Key（可选，有默认值）
export MINIMAX_API_KEY="your-key"

# 启动所有服务
docker-compose up -d

# 访问
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方式2: 本地开发

**后端:**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**前端:**
```bash
cd frontend
npm install
npm run dev
```

## 功能

- [x] 输入问题，获取多Agent辩论结果
- [x] 选择不同的Agent组合策略（标注认知维度冲突）
- [x] 实时查看辩论过程和置信度
- [x] 查看16种MBTI Agent类型介绍
- [x] AI模型选择（MiniMax/GPT-4/Claude/Mock）
- [x] API配置面板（可自定义模型API）
- [x] 多维评估指标（置信度、观点分歧度、Krippendorff α）
- [x] 流式响应（SSE）
- [ ] 历史记录（开发中）

## API接口

| 方法 | 路径 | 说明 |
|-----|------|------|
| GET | `/` | API信息 |
| GET | `/agents` | 获取所有Agent类型 |
| GET | `/combinations` | 获取Agent组合策略（含认知维度） |
| POST | `/solve` | 解决问题（支持X-API-Config自定义API） |
| POST | `/solve/stream` | 流式解决问题（SSE） |
| GET | `/tasks/{id}` | 获取任务状态 |
| GET | `/health` | 健康检查 |

### 自定义API配置

通过 `X-API-Config` header传递JSON配置：

```json
{
  "provider": "minimax",
  "apiKey": "your-key",
  "baseUrl": "http://...",
  "model": "MiniMax-M2.7"
}
```

## 技术栈

- **后端**: FastAPI + Python 3.11
- **前端**: React + Vite + TypeScript + TailwindCSS
- **API**: REST + Server-Sent Events

## 目录结构

```
mbti-multi-agent-web/
├── backend/
│   ├── app/
│   │   └── main.py          # FastAPI入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # 主组件
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```