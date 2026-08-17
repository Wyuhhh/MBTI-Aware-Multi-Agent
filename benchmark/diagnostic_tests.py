"""
MBTI认知差异诊断测试题

专门设计用来验证：同质Agent vs 异质Agent是否产生真实认知差异
而非只是表面风格差异
"""

DIAGNOSTIC_TESTS = {
    "T_F_dimension": {
        "name": "T-F维度测试",
        "description": "测试逻辑(T) vs 情感(F) 的真实认知差异",
        "questions": [
            {
                "id": "TF001",
                "question": "公司裁员20%可以提升效率，但会影响很多家庭。你作为决策者，怎么做？",
                "expected_T_response": "基于ROI和长期生存能力做决策，情感因素不应影响商业判断",
                "expected_F_response": "寻找两者兼顾的方案，如分阶段裁员、提供安置支持等",
            },
            {
                "id": "TF002",
                "question": "朋友创业失败向你借钱，你说？",
                "expected_T_response": "评估投资回报率和机会成本，不因情感影响判断",
                "expected_F_response": "先考虑朋友的需求和感受，再考虑其他因素",
            },
            {
                "id": "TF003",
                "question": "一个天才程序员但难以合作的员工，要不要开除？",
                "expected_T_response": "如果产出足够覆盖其造成的成本，可保留；否则应开除",
                "expected_F_response": "尝试调解，了解其难以合作的原因，给改进机会",
            },
            {
                "id": "TF004",
                "question": "客户要求你修改已验收的合同条款，你怎么办？",
                "expected_T_response": "按合同执行，修改需另签补充协议",
                "expected_F_response": "考虑长期关系，在合理范围内让步",
            },
            {
                "id": "TF005",
                "question": "你的决定被证明是错误的，团队成员当众批评你，你怎么反应？",
                "expected_T_response": "承认错误，分析原因，调整策略",
                "expected_F_response": "先理解团队情绪，私下再讨论改进",
            },
        ],
    },

    "N_S_dimension": {
        "name": "N-S维度测试",
        "description": "测试直觉(N) vs 实感(S) 的真实认知差异",
        "questions": [
            {
                "id": "NS001",
                "question": "预测10年后最火的行业是什么？",
                "expected_N_response": "基于技术趋势和社会变革推演，如AI、生物技术等",
                "expected_S_response": "基于当前数据和近期趋势，如消费、医疗等",
            },
            {
                "id": "NS002",
                "question": "描述你理想中的家是什么样的？",
                "expected_N_response": "强调理念、氛围、精神意义",
                "expected_S_response": "具体描述布局、摆设、功能区",
            },
            {
                "id": "NS003",
                "question": "看到一个新产品的第一反应是什么？",
                "expected_N_response": "这个产品能带来什么可能性？改变什么？",
                "expected_S_response": "多少钱？怎么用？质量如何？",
            },
            {
                "id": "NS004",
                "question": "如何学习一门新技能？",
                "expected_N_response": "先理解底层原理和框架，再实践",
                "expected_S_response": "先照着做，从实践中学习",
            },
            {
                "id": "NS005",
                "question": "你读小说时关注什么？",
                "expected_N_response": "主题、隐喻、可能性、作者想表达什么",
                "expected_S_response": "情节、人物、具体场景描写",
            },
        ],
    },

    "J_P_dimension": {
        "name": "J-P维度测试",
        "description": "测试判断(J) vs 感知(P) 的真实认知差异",
        "questions": [
            {
                "id": "JP001",
                "question": "计划周末出行，你会怎么做？",
                "expected_J_response": "提前订好行程、餐厅、景点门票",
                "expected_P_response": "到时再说，保持灵活性",
            },
            {
                "id": "JP002",
                "question": "收到请柬说'时间地点待定'，你的反应是？",
                "expected_J_response": "不舒服，没有明确信息如何安排",
                "expected_P_response": "没关系，到时看情况",
            },
            {
                "id": "JP003",
                "question": "项目deadline还有一周，进度正常，你会？",
                "expected_J_response": "开始规划收尾工作，确保万无一失",
                "expected_P_response": "按目前节奏进行，最后再冲刺",
            },
            {
                "id": "JP004",
                "question": "做决定时你更看重什么？",
                "expected_J_response": "速度和确定性 - 决定了就执行",
                "expected_P_response": "开放性 - 保留调整空间",
            },
            {
                "id": "JP005",
                "question": "对方约会迟到30分钟，你会？",
                "expected_J_response": "已经等得焦虑，可能会打电话催促",
                "expected_P_response": "无所谓，利用时间做点别的",
            },
        ],
    },

    "E_I_dimension": {
        "name": "E-I维度测试",
        "description": "测试外向(E) vs 内向(I) 的真实认知差异",
        "questions": [
            {
                "id": "EI001",
                "question": "加班到很晚回家前，你最想做的是？",
                "expected_E_response": "找个朋友聊聊，今天发生的事",
                "expected_P_response": "一个人安静待会儿，恢复能量",
            },
            {
                "id": "EI002",
                "question": "在陌生聚会上，你通常会？",
                "expected_E_response": "主动和陌生人搭话，很快认识新朋友",
                "expected_P_response": "找认识的人待着，或安静观察",
            },
            {
                "id": "EI003",
                "question": "工作累了，你的充电方式是？",
                "expected_E_response": "和朋友出去浪，社交让我恢复精力",
                "expected_P_response": "一个人待着，看书、听音乐",
            },
            {
                "id": "EI004",
                "question": "需要做决策时，你更倾向于？",
                "expected_E_response": "和别人讨论，听取多方意见",
                "expected_P_response": "自己思考清楚再下定论",
            },
            {
                "id": "EI005",
                "question": "旅行时你更喜欢？",
                "expected_E_response": "热门景点、人多的地方，感受热闹",
                "expected_P_response": "小众目的地、人少的地方，享受宁静",
            },
        ],
    },

    "cross_dimension": {
        "name": "跨维度测试",
        "description": "测试复杂场景下多维度的综合表现",
        "questions": [
            {
                "id": "CROSS001",
                "question": "你的朋友被公司冤枉要开除，来向你哭诉，你会？",
                "dimensions": ["T_F", "E_I"],
                "expected_intjs": "分析情况，提供客观建议",
                "expected_enfps": "先共情陪伴，再一起想对策",
                "expected_istjs": "了解事实经过，帮助收集证据",
                "expected_esfps": "先安慰情绪，约出来散心",
            },
            {
                "id": "CROSS002",
                "question": "老板突然要求你明天做一个你完全不懂的方案的汇报，你怎么办？",
                "dimensions": ["T_F", "J_P"],
                "expected_intjs": "快速学习核心要点，构建框架，准备接受提问",
                "expected_enfps": "和老板商量争取更多时间，或找人帮忙",
                "expected_istjs": "按已知信息如实汇报，承认局限性",
                "expected_esfps": "找同事帮忙，边学边讲",
            },
            {
                "id": "CROSS003",
                "question": "如何让一个沉闷的团队活跃起来？",
                "dimensions": ["E_I", "N_S"],
                "expected_intjs": "重新组织架构，设立明确目标激励",
                "expected_enfps": "搞活动激发创意，创造交流机会",
                "expected_istjs": "了解每个人，找到问题根源",
                "expected_esfps": "组织聚餐、游戏，创造轻松氛围",
            },
        ],
    },
}


def get_all_diagnostic_questions() -> list:
    """获取所有诊断测试题"""
    all_questions = []
    for category, data in DIAGNOSTIC_TESTS.items():
        for q in data["questions"]:
            all_questions.append({
                **q,
                "category": category,
                "dimension": data["name"],
            })
    return all_questions


def get_diagnostic_questions_by_dimension(dimension: str) -> list:
    """按维度获取诊断测试题"""
    if dimension in DIAGNOSTIC_TESTS:
        return DIAGNOSTIC_TESTS[dimension]["questions"]
    return []


def get_question_count() -> dict:
    """获取各维度问题数量"""
    return {
        dimension: len(data["questions"])
        for dimension, data in DIAGNOSTIC_TESTS.items()
    }


if __name__ == "__main__":
    total = get_all_diagnostic_questions()
    print(f"诊断测试题总数: {len(total)}")
    print("\n各维度问题数:")
    for dim, count in get_question_count().items():
        print(f"  {dim}: {count} 题")