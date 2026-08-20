"""
MBTI Multi-Agent Web API
FastAPI后端
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import json
import uuid
import os

# 导入原有的Agent系统 - 确保路径正确
import sys
from pathlib import Path

# 添加mbti-multi-agent到path (用于直接运行)
mbti_path = Path(__file__).parent.parent.parent / "mbti-multi-agent"
if not mbti_path.exists():
    # 尝试上一级目录（开发环境）
    mbti_path = Path(__file__).parent.parent.parent.parent / "mbti-multi-agent"
if str(mbti_path) not in sys.path:
    sys.path.insert(0, str(mbti_path))

# 设置PYTHONPATH环境变量确保子进程也能找到
os.environ["PYTHONPATH"] = str(mbti_path) + os.pathsep + os.environ.get("PYTHONPATH", "")

from src.llm.client import MiniMaxClient, MockLLMClient
from src.main import MBTIMultiAgentSystem


# ============== Pydantic Models ==============

class SolveRequest(BaseModel):
    query: str
    task_type: Optional[str] = None
    agent_types: Optional[List[str]] = None
    use_streaming: bool = False
    model: Optional[str] = "MiniMax-M2.7"  # 支持选择模型


class AgentInfo(BaseModel):
    id: str
    mbti_type: str
    name: str
    core_traits: List[str]


class SolveResponse(BaseModel):
    task_id: str
    consensus: str
    alternatives: List[str]
    reasoning_chain: str
    empathy_examples: List[str]
    dimension_analysis: Dict[str, str]
    agents_info: List[AgentInfo]
    confidence: float
    voting_result: str
    full_summary: str
    timestamp: str
    # 新增评估指标
    viewpoint_divergence: float = 0.0  # 观点分歧度 (0-1, 越高表示分歧越大)
    krippendorff_alpha: float = 0.0  # Krippendorff α系数


class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float  # 0.0 - 1.0
    result: Optional[SolveResponse] = None
    error: Optional[str] = None


# ============== FastAPI App ==============

app = FastAPI(
    title="MBTI Multi-Agent API",
    description="MBTI人格多智能体辩论系统 Web API",
    version="1.0.0",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局配置
LLM_PROVIDER = "minimax"
LLM_API_KEY = "sk-cp-ZCwysUdUK1bPpueFdYe-yr97Q9-mRKFFNP8q1WYNcsIBrR_eT9nuHWEz0EKPPy3s7xAjvUvUCxcf_jShb6XCd674oPOZm5aantIXyAn4Fexo-qTYyNhvxkc"
LLM_BASE_URL = "http://10.68.46.180:31943"
LLM_MODEL = "MiniMax-M2.7"

USE_MOCK = False  # 设为True则使用Mock

# 任务存储（生产环境应该用数据库）
tasks: Dict[str, TaskStatus] = {}


# ============== 辅助函数 ==============

# 支持的模型列表
AVAILABLE_MODELS = {
    "MiniMax-M2.7": {
        "name": "MiniMax-M2.7",
        "provider": "minimax",
        "description": "MiniMax M2.7 模型",
    },
    "gpt-4": {
        "name": "GPT-4",
        "provider": "openai",
        "description": "OpenAI GPT-4",
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "provider": "openai",
        "description": "OpenAI GPT-3.5 Turbo",
    },
    "claude-3-opus": {
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "description": "Anthropic Claude 3 Opus",
    },
    "claude-3-sonnet": {
        "name": "Claude 3 Sonnet",
        "provider": "anthropic",
        "description": "Anthropic Claude 3 Sonnet",
    },
    "mock": {
        "name": "Mock (测试)",
        "provider": "mock",
        "description": "模拟响应，用于测试",
    },
}


def get_llm_client(model: str = "MiniMax-M2.7", api_key: str = None, base_url: str = None):
    """获取LLM客户端"""
    if api_key is None:
        api_key = LLM_API_KEY
    if base_url is None:
        base_url = LLM_BASE_URL

    # 统一转为小写检查
    model_lower = model.lower()
    if "mock" in model_lower or USE_MOCK:
        return MockLLMClient()

    # MiniMax模型使用Anthropic兼容接口
    if model_lower.startswith("minimax") or model.startswith("MiniMax"):
        from src.llm.client import AnthropicClient
        return AnthropicClient(
            api_key=api_key,
            model=model,
            base_url=base_url + "/anthropic/v1" if "/anthropic" not in base_url else base_url,
        )

    if model.startswith("gpt"):
        from src.llm.client import OpenAIClient
        return OpenAIClient(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    elif model.startswith("claude"):
        from src.llm.client import AnthropicClient
        return AnthropicClient(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )
    else:
        # 默认MiniMax
        return MiniMaxClient(
            api_key=api_key,
            model=model,
            base_url=base_url,
        )


def get_mbti_system(model: str = "MiniMax-M2.7", api_key: str = None, base_url: str = None):
    """获取MBTI系统"""
    llm_client = get_llm_client(model, api_key, base_url)
    return MBTIMultiAgentSystem(llm_client=llm_client)


# ============== API Routes ==============

@app.get("/")
async def root():
    """API首页"""
    return {
        "name": "MBTI Multi-Agent API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/agents")
async def list_agents():
    """获取所有可用的MBTI Agent类型"""
    return {
        "agents": [
            {"type": "INTJ", "name": "战略家", "description": "逻辑驱动，擅长长远规划"},
            {"type": "INTP", "name": "逻辑学家", "description": "抽象分析，追求理论完备"},
            {"type": "ENTJ", "name": "指挥官", "description": "果断决策，驱动行动"},
            {"type": "ENTP", "name": "辩论家", "description": "辩证思维，挑战现状"},
            {"type": "INFJ", "name": "提倡者", "description": "共情洞察，关注价值"},
            {"type": "INFP", "name": "调停者", "description": "理想主义，忠于内心"},
            {"type": "ENFJ", "name": "主人公", "description": "激励人心，推动共识"},
            {"type": "ENFP", "name": "竞选者", "description": "热情创造，探索可能"},
            {"type": "ISTJ", "name": "检查员", "description": "务实可靠，遵循规则"},
            {"type": "ISFJ", "name": "守护者", "description": "忠诚奉献，关注细节"},
            {"type": "ESTJ", "name": "执行者", "description": "高效务实，维护秩序"},
            {"type": "ESFJ", "name": "提供者", "description": "热情助人，构建和谐"},
            {"type": "ISTP", "name": "手艺人", "description": "灵活务实，擅长技术"},
            {"type": "ISFP", "name": "艺术家", "description": "敏感审美，珍惜自由"},
            {"type": "ESTP", "name": "企业家", "description": "冒险实践，把握当下"},
            {"type": "ESFP", "name": "表演者", "description": "热情社交，享受生活"},
        ]
    }


@app.get("/models")
async def list_models():
    """获取所有可用的AI模型"""
    return {
        "models": list(AVAILABLE_MODELS.values()),
        "default": "MiniMax-M2.7",
    }


@app.get("/combinations")
async def list_combinations():
    """获取预置的Agent组合策略（按认知维度冲突分类）"""
    return {
        "combinations": [
            {
                "id": "career_planning",
                "name": "职业发展型",
                "agents": ["INTJ", "ENFP", "ISTJ"],
                "dimensions": ["战略眼光", "可能性探索", "务实执行"],
                "conflict": "N-S (直觉/感觉) + J-P (判断/知觉)",
                "description": "适合职业发展、考研/工作选择、岗位选择等规划类问题",
            },
            {
                "id": "ethical_dilemma",
                "name": "伦理判断型",
                "agents": ["INFJ", "ESTP", "INTP"],
                "dimensions": ["价值共情", "实践洞察", "逻辑分析"],
                "conflict": "T-F (思考/情感) + N-S (直觉/感觉)",
                "description": "适合道德判断、价值取舍、两难选择等伦理问题",
            },
            {
                "id": "product_decision",
                "name": "产品决策型",
                "agents": ["ENTP", "ISTJ", "ESFJ"],
                "dimensions": ["创新辩证", "细节执行", "用户共情"],
                "conflict": "N-S (直觉/感觉) + T-F (思考/情感)",
                "description": "适合产品功能优先级、商业决策、用户需求分析等问题",
            },
            {
                "id": "tech_solution",
                "name": "技术方案型",
                "agents": ["INTP", "ISTJ", "ENTJ"],
                "dimensions": ["理论分析", "务实落地", "高效执行"],
                "conflict": "N-S (直觉/感觉) + J-P (判断/知觉)",
                "description": "适合技术选型、系统架构设计、技术难点攻关等问题",
            },
            {
                "id": "creative_ideation",
                "name": "创意发散型",
                "agents": ["ENFP", "ENTP", "ESFP"],
                "dimensions": ["热情创造", "辩证挑战", "实践验证"],
                "conflict": "N-S (直觉/感觉) + J-P (判断/知觉)",
                "description": "适合头脑风暴、创意生成、探索新方向等问题",
            },
            {
                "id": "risk_assessment",
                "name": "风险评估型",
                "agents": ["INTJ", "ISTJ", "ESTP"],
                "dimensions": ["战略预见", "细节把控", "冒险实践"],
                "conflict": "N-S (直觉/感觉) + T-F (思考/情感)",
                "description": "适合风险分析、预案规划、商业可行性评估等问题",
            },
            {
                "id": "team_coordination",
                "name": "团队协调型",
                "agents": ["ENFJ", "ESFJ", "ISTJ"],
                "dimensions": ["激励引领", "服务关怀", "规范执行"],
                "conflict": "T-F (思考/情感) + J-P (判断/知觉)",
                "description": "适合团队管理、人员协调、文化建设、冲突调解等问题",
            },
            {
                "id": "strategic_planning",
                "name": "战略规划型",
                "agents": ["INTJ", "ENTJ", "INFJ"],
                "dimensions": ["战略布局", "果断决策", "远见共情"],
                "conflict": "T-F (思考/情感) + N-S (直觉/感觉)",
                "description": "适合公司战略、长期规划、市场布局等高层决策问题",
            },
        ]
    }


@app.post("/solve", response_model=SolveResponse)
async def solve(request_data: SolveRequest, request: Request):
    """解决问题 - 核心API"""
    task_id = str(uuid.uuid4())[:8]

    # 创建任务状态
    tasks[task_id] = TaskStatus(
        task_id=task_id,
        status="running",
        progress=0.0,
    )

    try:
        # 尝试从header获取API配置
        api_config_header = request.headers.get('X-API-Config')
        effective_api_key = LLM_API_KEY
        effective_base_url = LLM_BASE_URL
        # 模型优先使用请求体中的选择，X-API-Config只提供api_key和base_url
        model = request_data.model or LLM_MODEL

        if api_config_header:
            try:
                user_config = json.loads(api_config_header)
                # X-API-Config只覆盖api_key和base_url，不覆盖model
                if user_config.get('apiKey'):
                    effective_api_key = user_config['apiKey']
                if user_config.get('baseUrl'):
                    effective_base_url = user_config['baseUrl']
            except json.JSONDecodeError:
                pass  # 使用默认配置

        # 获取MBTI系统
        system = get_mbti_system(model=model, api_key=effective_api_key, base_url=effective_base_url)

        # 更新进度
        tasks[task_id].progress = 0.1

        # 解决问题
        result = system.solve(
            query=request_data.query,
            task_type=request_data.task_type,
            agent_types=request_data.agent_types,
            auto_task_detection=request_data.task_type is None,
        )

        # 更新进度
        tasks[task_id].progress = 0.9

        # 获取评估指标
        viewpoint_divergence = 0.0
        krippendorff_alpha = 0.0
        if system.current_voting_result:
            viewpoint_divergence = system.current_voting_result.viewpoint_divergence
            krippendorff_alpha = system.current_voting_result.krippendorff_alpha

        # 构建响应
        response = SolveResponse(
            task_id=task_id,
            consensus=result["consensus"],
            alternatives=result["alternatives"],
            reasoning_chain=result["reasoning_chain"],
            empathy_examples=result["empathy_examples"],
            dimension_analysis=result["dimension_analysis"],
            agents_info=[
                AgentInfo(**a) for a in result["agents_info"]
            ],
            confidence=result["confidence"],
            voting_result=result["voting_result"],
            full_summary=result["full_summary"],
            timestamp=datetime.now().isoformat(),
            viewpoint_divergence=viewpoint_divergence,
            krippendorff_alpha=krippendorff_alpha,
        )

        # 完成
        tasks[task_id].status = "completed"
        tasks[task_id].progress = 1.0
        tasks[task_id].result = response

        return response

    except Exception as e:
        tasks[task_id].status = "failed"
        tasks[task_id].error = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/solve/stream")
async def solve_stream(request: SolveRequest):
    """流式解决问题 - 返回Server-Sent Events"""
    task_id = str(uuid.uuid4())[:8]

    async def event_generator():
        try:
            system = get_mbti_system()

            # 开始
            yield f"event: status\ndata: {json.dumps({'task_id': task_id, 'status': 'running', 'progress': 0.1})}\n\n"

            # 解决
            yield f"event: status\ndata: {json.dumps({'task_id': task_id, 'status': 'running', 'progress': 0.5})}\n\n"

            result = system.solve(
                query=request.query,
                task_type=request.task_type,
                agent_types=request.agent_types,
                auto_task_detection=request.task_type is None,
            )

            # 完成
            yield f"event: status\ndata: {json.dumps({'task_id': task_id, 'status': 'completed', 'progress': 1.0})}\n\n"

            # 发送结果
            yield f"event: result\ndata: {json.dumps({
                'consensus': result['consensus'][:500],
                'agents': [a['mbti_type'] for a in result['agents_info']],
                'confidence': result['confidence'],
            })}\n\n"

        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/tasks/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """获取任务状态"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============== 启动 ==============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)