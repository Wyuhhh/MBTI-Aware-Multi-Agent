"""
200题评测集

分类:
- career_planning (25题): 职业规划
- ethical_dilemma (25题): 伦理困境
- product_decision (25题): 产品决策
- tech_solution (25题): 技术方案
- creative_ideation (25题): 创意发散
- risk_assessment (25题): 风险评估
- team_coordination (25题): 团队协调
- strategic_planning (25题): 战略规划
"""

EVALUATION_DATASET = [
    # ============ career_planning (25题) ============
    {"id": "CP001", "category": "career_planning", "question": "我应该在考研和工作之间如何选择？"},
    {"id": "CP002", "category": "career_planning", "question": "转行到AI领域是否明智，需要准备什么？"},
    {"id": "CP003", "category": "career_planning", "question": "大公司螺丝钉 vs 小公司核心员工，如何选择？"},
    {"id": "CP004", "category": "career_planning", "question": "35岁程序员应该转管理还是继续深耕技术？"},
    {"id": "CP005", "category": "career_planning", "question": "如何判断一家创业公司是否值得加入？"},
    {"id": "CP006", "category": "career_planning", "question": "offer比较：薪资高但996 vs 薪资低但955？"},
    {"id": "CP007", "category": "career_planning", "question": "工作5年想出国读书，值不值得？"},
    {"id": "CP008", "category": "career_planning", "question": "内向的人适合做产品经理吗？"},
    {"id": "CP009", "category": "career_planning", "question": "如何规划自己的职业发展路径？"},
    {"id": "CP010", "category": "career_planning", "question": "接到了不太喜欢的公司的offer，该去吗？"},
    {"id": "CP011", "category": "career_planning", "question": "30岁开始学编程还来得及吗？"},
    {"id": "CP012", "category": "career_planning", "question": "如何判断是否该跳槽了？"},
    {"id": "CP013", "category": "career_planning", "question": "自由职业者如何规划职业发展？"},
    {"id": "CP014", "category": "career_planning", "question": "技术和管理路线应该如何选择？"},
    {"id": "CP015", "category": "career_planning", "question": "远程工作机会要不要接受？"},
    {"id": "CP016", "category": "career_planning", "question": "如何在试用期判断公司是否适合自己？"},
    {"id": "CP017", "category": "career_planning", "question": "应届毕业生第一份工作有多重要？"},
    {"id": "CP018", "category": "career_planning", "question": "跨行业跳槽需要注意什么？"},
    {"id": "CP019", "category": "career_planning", "question": "如何利用业余时间发展副业？"},
    {"id": "CP020", "category": "career_planning", "question": "工作与生活平衡重要还是晋升机会重要？"},
    {"id": "CP021", "category": "career_planning", "question": "被裁员后应该如何应对？"},
    {"id": "CP022", "category": "career_planning", "question": "如何评估一份工作的发展前景？"},
    {"id": "CP023", "category": "career_planning", "question": "女性在科技行业如何规划职业发展？"},
    {"id": "CP024", "category": "career_planning", "question": "是继续深耕当前领域还是拓展新技能？"},
    {"id": "CP025", "category": "career_planning", "question": "如何为自己的职业生涯设立短期和长期目标？"},

    # ============ ethical_dilemma (25题) ============
    {"id": "ED001", "category": "ethical_dilemma", "question": "发现同事在报销中夹杂了一些不该报销的费用，应该举报吗？"},
    {"id": "ED002", "category": "ethical_dilemma", "question": "朋友托你帮忙在简历中夸大经历，应该答应吗？"},
    {"id": "ED003", "category": "ethical_dilemma", "question": "公司让你修改数据让报告更好看，你怎么办？"},
    {"id": "ED004", "category": "ethical_dilemma", "question": "知道上司要炒掉某个同事，要不要提前告诉他？"},
    {"id": "ED005", "category": "ethical_dilemma", "question": "发现产品有安全隐患但公司选择隐瞒，用户利益vs公司利益如何抉择？"},
    {"id": "ED006", "category": "ethical_dilemma", "question": "朋友问你打听竞争对手的商业机密，你怎么办？"},
    {"id": "ED007", "category": "ethical_dilemma", "question": "试用期被要求做有违职业道德的事，应该忍还是走？"},
    {"id": "ED008", "category": "ethical_dilemma", "question": "AI生成内容涉及版权问题，应该如何处理？"},
    {"id": "ED009", "category": "ethical_dilemma", "question": "是否应该为了业绩向客户过度承诺？"},
    {"id": "ED010", "category": "ethical_dilemma", "question": "发现团队在加班赶工期但质量堪忧，公开提出还是保持沉默？"},
    {"id": "ED011", "category": "ethical_dilemma", "question": "用公司资源做自己的副业被发现，应该如何解释？"},
    {"id": "ED012", "category": "ethical_dilemma", "question": "面试时发现公司在招聘中歧视某类人群，应该加入吗？"},
    {"id": "ED013", "category": "ethical_dilemma", "question": "是否应该告诉用户产品存在已知缺陷？"},
    {"id": "ED014", "category": "ethical_dilemma", "question": "朋友喝醉后说了公司机密给你听，你应该怎么做？"},
    {"id": "ED015", "category": "ethical_dilemma", "question": "为了赢得项目，竞争对手故意抹黑你们，你怎么应对？"},
    {"id": "ED016", "category": "ethical_dilemma", "question": "是否应该为了效率而牺牲一些员工的福利？"},
    {"id": "ED017", "category": "ethical_dilemma", "question": "发现团队招聘存在性别歧视，要不要揭发？"},
    {"id": "ED018", "category": "ethical_dilemma", "question": "AI决策系统导致了不公平结果，谁应该负责？"},
    {"id": "ED019", "category": "ethical_dilemma", "question": "是否应该用裁员省下的钱给留下的员工发奖金？"},
    {"id": "ED020", "category": "ethical_dilemma", "question": "供应商给回扣，团队其他人都默许接受，你怎么办？"},
    {"id": "ED021", "category": "ethical_dilemma", "question": "用户数据被泄露，但公司选择不公开道歉，应该怎么办？"},
    {"id": "ED022", "category": "ethical_dilemma", "question": "是否应该为了公司利益而对投资者隐瞒部分信息？"},
    {"id": "ED023", "category": "ethical_dilemma", "question": "同事在工作中受伤但选择不报告，公司应该承担责任吗？"},
    {"id": "ED024", "category": "ethical_dilemma", "question": "是否应该为了赶进度而降低代码质量标准？"},
    {"id": "ED025", "category": "ethical_dilemma", "question": "发现导师剽窃学生论文成果，作为同事应该如何处理？"},

    # ============ product_decision (25题) ============
    {"id": "PD001", "category": "product_decision", "question": "是否应该在APP中加入社交功能来增加用户粘性？"},
    {"id": "PD002", "category": "product_decision", "question": "免费增值模式 vs 订阅制，哪个更适合我们的产品？"},
    {"id": "PD003", "category": "product_decision", "question": "是否应该开发PC端应用还是专注移动端？"},
    {"id": "PD004", "category": "product_decision", "question": "是否应该收购竞争对手来快速扩张市场？"},
    {"id": "PD005", "category": "product_decision", "question": "产品是否应该做国际化，还是先深耕国内市场？"},
    {"id": "PD006", "category": "product_decision", "question": "是否应该采用黑暗模式作为默认主题？"},
    {"id": "PD007", "category": "product_decision", "question": "是追求功能全面还是专注核心功能做到极致？"},
    {"id": "PD008", "category": "product_decision", "question": "是否应该引入广告作为盈利模式？"},
    {"id": "PD009", "category": "product_decision", "question": "AI助手功能应该作为免费功能还是付费高级功能？"},
    {"id": "PD010", "category": "product_decision", "question": "是否应该开放API给第三方开发者？"},
    {"id": "PD011", "category": "product_decision", "question": "用户反馈和老板需求冲突时，应该听谁的？"},
    {"id": "PD012", "category": "product_decision", "question": "是否应该做小程序版本还是只做独立APP？"},
    {"id": "PD013", "category": "product_decision", "question": "是否应该在产品中加入游戏化元素？"},
    {"id": "PD014", "category": "product_decision", "question": "是优先提升用户体验还是优化变现能力？"},
    {"id": "PD015", "category": "product_decision", "question": "是否应该开发面向企业客户(B2B)的版本？"},
    {"id": "PD016", "category": "product_decision", "question": "是否应该采用Material Design还是自定义设计语言？"},
    {"id": "PD017", "category": "product_decision", "question": "推送通知应该默认开启还是关闭？"},
    {"id": "PD018", "category": "product_decision", "question": "是否应该让用户自定义界面布局？"},
    {"id": "PD019", "category": "product_decision", "question": "是快速迭代发布还是憋大招一次性发布大版本？"},
    {"id": "PD020", "category": "product_decision", "question": "是否应该引入会员分级制度？"},
    {"id": "PD021", "category": "product_decision", "question": "是专注提升新用户转化还是深耕老用户留存？"},
    {"id": "PD022", "category": "product_decision", "question": "是否应该接入第三方登录还是只支持自建账号体系？"},
    {"id": "PD023", "category": "product_decision", "question": "是继续维护老产品还是投入全部资源开发新产品？"},
    {"id": "PD024", "category": "product_decision", "question": "是否应该在产品中引入AI推荐系统？"},
    {"id": "PD025", "category": "product_decision", "question": "是追求下载量还是追求付费转化率？"},

    # ============ tech_solution (25题) ============
    {"id": "TS001", "category": "tech_solution", "question": "微服务架构 vs 单体架构，如何选择？"},
    {"id": "TS002", "category": "tech_solution", "question": "关系型数据库 vs NoSQL，技术选型建议是什么？"},
    {"id": "TS003", "category": "tech_solution", "question": "React vs Vue，前端框架应该如何选择？"},
    {"id": "TS004", "category": "tech_solution", "question": "是使用云服务还是自建机房？"},
    {"id": "TS005", "category": "tech_solution", "question": "是否应该引入Kubernetes进行容器编排？"},
    {"id": "TS006", "category": "tech_solution", "question": "GraphQL vs REST API，设计选择是什么？"},
    {"id": "TS007", "category": "tech_solution", "question": "是使用SaaS服务还是自己开发？"},
    {"id": "TS008", "category": "tech_solution", "question": "如何设计高可用的系统架构？"},
    {"id": "TS009", "category": "tech_solution", "question": "MySQL vs PostgreSQL，应该用哪个？"},
    {"id": "TS010", "category": "tech_solution", "question": "是采用敏捷开发还是瀑布模型？"},
    {"id": "TS011", "category": "tech_solution", "question": "是否应该引入CI/CD流水线？"},
    {"id": "TS012", "category": "tech_solution", "question": "如何处理系统的高并发问题？"},
    {"id": "TS013", "category": "tech_solution", "question": "是使用Redis还是Memcached做缓存？"},
    {"id": "TS014", "category": "tech_solution", "question": "是否应该引入服务网格(Service Mesh)？"},
    {"id": "TS015", "category": "tech_solution", "question": "Python vs Go，后端语言选择建议？"},
    {"id": "TS016", "category": "tech_solution", "question": "如何设计数据库分库分表策略？"},
    {"id": "TS017", "category": "tech_solution", "question": "是使用消息队列还是同步调用？"},
    {"id": "TS018", "category": "tech_solution", "question": "是否应该引入自动化测试，覆盖率目标多少合适？"},
    {"id": "TS019", "category": "tech_solution", "question": "Monorepo vs Polyrepo，代码库组织方式选择？"},
    {"id": "TS020", "category": "tech_solution", "question": "如何设计API版本管理策略？"},
    {"id": "TS021", "category": "tech_solution", "question": "是使用Elasticsearch还是自建搜索？"},
    {"id": "TS022", "category": "tech_solution", "question": "如何保障代码质量和团队协作效率？"},
    {"id": "TS023", "category": "tech_solution", "question": "是否应该引入代码审查(Code Review)制度？"},
    {"id": "TS024", "category": "tech_solution", "question": "是使用Serverless还是传统服务器架构？"},
    {"id": "TS025", "category": "tech_solution", "question": "如何选择合适的日志监控系统？"},

    # ============ creative_ideation (25题) ============
    {"id": "CI001", "category": "creative_ideation", "question": "如何让老年人也能轻松使用我们的APP？"},
    {"id": "CI002", "category": "creative_ideation", "question": "有哪些创新的方式可以提高用户留存率？"},
    {"id": "CI003", "category": "creative_ideation", "question": "如何用AI技术改造传统行业？"},
    {"id": "CI004", "category": "creative_ideation", "question": "有哪些方法可以降低用户学习成本？"},
    {"id": "CI005", "category": "creative_ideation", "question": "如何让产品更有趣，吸引年轻用户？"},
    {"id": "CI006", "category": "creative_ideation", "question": "有哪些创新的商业模式可以尝试？"},
    {"id": "CI007", "category": "creative_ideation", "question": "如何利用AR/VR技术提升用户体验？"},
    {"id": "CI008", "category": "creative_ideation", "question": "如何设计一个让人上瘾的产品？"},
    {"id": "CI009", "category": "creative_ideation", "question": "有哪些方法可以帮助用户形成好习惯？"},
    {"id": "CI010", "category": "creative_ideation", "question": "如何让用户主动帮我们传播产品？"},
    {"id": "CI011", "category": "creative_ideation", "question": "有哪些被忽视的用户痛点可以解决？"},
    {"id": "CI012", "category": "creative_ideation", "question": "如何将线下体验数字化？"},
    {"id": "CI013", "category": "creative_ideation", "question": "有哪些方式可以让产品更加个性化？"},
    {"id": "CI014", "category": "creative_ideation", "question": "如何利用社交网络效应实现增长？"},
    {"id": "CI015", "category": "creative_ideation", "question": "有哪些创新的支付方式可以提升转化率？"},
    {"id": "CI016", "category": "creative_ideation", "question": "如何让产品设计更具包容性？"},
    {"id": "CI017", "category": "creative_ideation", "question": "有哪些方法可以提升用户参与度？"},
    {"id": "CI018", "category": "creative_ideation", "question": "如何将订阅制和一次性买断制结合？"},
    {"id": "CI019", "category": "creative_ideation", "question": "有哪些方式可以利用用户生成内容？"},
    {"id": "CI020", "category": "creative_ideation", "question": "如何设计一个成功的会员体系？"},
    {"id": "CI021", "category": "creative_ideation", "question": "有哪些创新的客服方式可以提升满意度？"},
    {"id": "CI022", "category": "creative_ideation", "question": "如何让产品在不同文化背景下都能受欢迎？"},
    {"id": "CI023", "category": "creative_ideation", "question": "有哪些方式可以降低用户流失率？"},
    {"id": "CI024", "category": "creative_ideation", "question": "如何设计一个成功的邀请奖励机制？"},
    {"id": "CI025", "category": "creative_ideation", "question": "有哪些方法可以提升品牌忠诚度？"},

    # ============ risk_assessment (25题) ============
    {"id": "RA001", "category": "risk_assessment", "question": "公司明年扩张一倍规模，可能面临哪些风险？"},
    {"id": "RA002", "category": "risk_assessment", "question": "引入AI技术可能带来哪些潜在风险？"},
    {"id": "RA003", "category": "risk_assessment", "question": "开拓海外市场需要防范哪些风险？"},
    {"id": "RA004", "category": "risk_assessment", "question": "过度依赖单一供应商有什么风险？"},
    {"id": "RA005", "category": "risk_assessment", "question": "员工集体离职可能带来哪些风险？"},
    {"id": "RA006", "category": "risk_assessment", "question": "技术架构转型可能遇到哪些风险？"},
    {"id": "RA007", "category": "risk_assessment", "question": "数据泄露事件会对公司造成什么影响？"},
    {"id": "RA008", "category": "risk_assessment", "question": "竞争对手融资成功对我们意味着什么风险？"},
    {"id": "RA009", "category": "risk_assessment", "question": "快速招聘大量新人有哪些潜在风险？"},
    {"id": "RA010", "category": "risk_assessment", "question": "政策监管变化可能带来哪些风险？"},
    {"id": "RA011", "category": "risk_assessment", "question": "价格战可能带来哪些风险？"},
    {"id": "RA012", "category": "risk_assessment", "question": "核心技术人员被挖走有哪些风险？"},
    {"id": "RA013", "category": "risk_assessment", "question": "系统迁移到云端有哪些风险需要防范？"},
    {"id": "RA014", "category": "risk_assessment", "question": "多元化扩张战略有哪些风险？"},
    {"id": "RA015", "category": "risk_assessment", "question": "供应链中断可能带来哪些风险？"},
    {"id": "RA016", "category": "risk_assessment", "question": "品牌声誉受损有哪些潜在风险？"},
    {"id": "RA017", "category": "risk_assessment", "question": "收购其他公司可能带来哪些整合风险？"},
    {"id": "RA018", "category": "risk_assessment", "question": "采用新技术路线有哪些风险？"},
    {"id": "RA019", "category": "risk_assessment", "question": "团队远程办公有哪些风险需要管理？"},
    {"id": "RA020", "category": "risk_assessment", "question": "客户集中度太高有哪些风险？"},
    {"id": "RA021", "category": "risk_assessment", "question": "现金流紧张可能带来哪些风险？"},
    {"id": "RA022", "category": "risk_assessment", "question": "产品线过度延伸有哪些风险？"},
    {"id": "RA023", "category": "risk_assessment", "question": "关键岗位缺乏备份有哪些风险？"},
    {"id": "RA024", "category": "risk_assessment", "question": "监管合规风险应该如何评估？"},
    {"id": "RA025", "category": "risk_assessment", "question": "经济下行周期有哪些风险需要防范？"},

    # ============ team_coordination (25题) ============
    {"id": "TC001", "category": "team_coordination", "question": "团队成员之间产生矛盾，应该如何调解？"},
    {"id": "TC002", "category": "team_coordination", "question": "如何处理能力强的刺头员工？"},
    {"id": "TC003", "category": "team_coordination", "question": "远程团队如何提升协作效率？"},
    {"id": "TC004", "category": "team_coordination", "question": "如何公平地分配棘手的任务？"},
    {"id": "TC005", "category": "team_coordination", "question": "团队技术栈转型时如何管理阻力？"},
    {"id": "TC006", "category": "team_coordination", "question": "如何处理团队内部的办公室政治？"},
    {"id": "TC007", "category": "team_coordination", "question": "新来的经理如何快速融入团队？"},
    {"id": "TC008", "category": "team_coordination", "question": "如何平衡团队成员之间的工作量？"},
    {"id": "TC009", "category": "team_coordination", "question": "团队目标和个人目标冲突时怎么办？"},
    {"id": "TC010", "category": "team_coordination", "question": "如何处理经常迟到的团队成员？"},
    {"id": "TC011", "category": "team_coordination", "question": "空降高管如何获得团队信任？"},
    {"id": "TC012", "category": "team_coordination", "question": "如何提升跨部门协作效率？"},
    {"id": "TC013", "category": "team_coordination", "question": "团队士气低落应该如何提振？"},
    {"id": "TC014", "category": "team_coordination", "question": "如何处理团队中的消极情绪？"},
    {"id": "TC015", "category": "team_coordination", "question": "如何公平地进行绩效评估？"},
    {"id": "TC016", "category": "team_coordination", "question": "团队出现小团体应该如何处理？"},
    {"id": "TC017", "category": "team_coordination", "question": "如何培养团队的后备人才？"},
    {"id": "TC018", "category": "team_coordination", "question": "996工作制下如何保持团队稳定？"},
    {"id": "TC019", "category": "team_coordination", "question": "如何处理团队成员的职业倦怠？"},
    {"id": "TC020", "category": "team_coordination", "question": "如何让团队成员接受建设性反馈？"},
    {"id": "TC021", "category": "team_coordination", "question": "如何平衡老员工和新员工的关系？"},
    {"id": "TC022", "category": "team_coordination", "question": "团队技术方案产生分歧如何决策？"},
    {"id": "TC023", "category": "team_coordination", "question": "如何提升团队的创新能力？"},
    {"id": "TC024", "category": "team_coordination", "question": "如何处理团队成员的个性化需求？"},
    {"id": "TC025", "category": "team_coordination", "question": "如何建立有效的团队沟通机制？"},

    # ============ strategic_planning (25题) ============
    {"id": "SP001", "category": "strategic_planning", "question": "公司未来3年应该如何规划发展路径？"},
    {"id": "SP002", "category": "strategic_planning", "question": "如何构建公司的核心竞争优势？"},
    {"id": "SP003", "category": "strategic_planning", "question": "是专注当前业务还是探索新增长点？"},
    {"id": "SP004", "category": "strategic_planning", "question": "如何应对竞争对手的低价策略？"},
    {"id": "SP005", "category": "strategic_planning", "question": "公司应该如何制定5年战略规划？"},
    {"id": "SP006", "category": "strategic_planning", "question": "是自建技术能力还是外包？"},
    {"id": "SP007", "category": "strategic_planning", "question": "如何打造有竞争力的组织文化？"},
    {"id": "SP008", "category": "strategic_planning", "question": "市场占有率重要还是利润率重要？"},
    {"id": "SP009", "category": "strategic_planning", "question": "如何制定合理的企业增长目标？"},
    {"id": "SP010", "category": "strategic_planning", "question": "是追求规模还是追求盈利？"},
    {"id": "SP011", "category": "strategic_planning", "question": "如何建立有效的战略执行机制？"},
    {"id": "SP012", "category": "strategic_planning", "question": "是否应该进行战略转型？"},
    {"id": "SP013", "category": "strategic_planning", "question": "如何平衡短期业绩和长期发展？"},
    {"id": "SP014", "category": "strategic_planning", "question": "是深耕细分市场还是追求规模化？"},
    {"id": "SP015", "category": "strategic_planning", "question": "如何构建企业护城河？"},
    {"id": "SP016", "category": "strategic_planning", "question": "数字化转型应该如何规划？"},
    {"id": "SP017", "category": "strategic_planning", "question": "如何制定有效的人才战略？"},
    {"id": "SP018", "category": "strategic_planning", "question": "是采取保守策略还是激进扩张？"},
    {"id": "SP019", "category": "strategic_planning", "question": "如何建立战略联盟实现共赢？"},
    {"id": "SP020", "category": "strategic_planning", "question": "如何应对行业颠覆性变革？"},
    {"id": "SP021", "category": "strategic_planning", "question": "是垂直整合还是聚焦核心能力？"},
    {"id": "SP022", "category": "strategic_planning", "question": "如何制定国际化战略？"},
    {"id": "SP023", "category": "strategic_planning", "question": "如何打造高效的组织架构？"},
    {"id": "SP024", "category": "strategic_planning", "question": "是追求技术领先还是市场领先？"},
    {"id": "SP025", "category": "strategic_planning", "question": "如何建立有效的风险管理体系？"},
]


def get_dataset():
    """获取完整数据集"""
    return EVALUATION_DATASET


def get_dataset_by_category(category: str):
    """按类别获取数据"""
    return [q for q in EVALUATION_DATASET if q["category"] == category]


def get_categories():
    """获取所有类别"""
    return list(set(q["category"] for q in EVALUATION_DATASET))


def get_question_count():
    """获取题目数量"""
    return len(EVALUATION_DATASET)


def get_category_stats():
    """获取各类别统计"""
    stats = {}
    for q in EVALUATION_DATASET:
        cat = q["category"]
        stats[cat] = stats.get(cat, 0) + 1
    return stats


if __name__ == "__main__":
    print(f"Total questions: {get_question_count()}")
    print(f"\nCategory stats:")
    for cat, count in get_category_stats().items():
        print(f"  {cat}: {count} questions")