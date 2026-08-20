import { useState, useEffect } from 'react'
import axios from 'axios'

// API base URL
const API_BASE = '/api'

// Types
interface Agent {
  type: string
  name: string
  description: string
}

interface Combination {
  id: string
  name: string
  agents: string[]
  description: string
  dimensions?: string[]  // 认知维度
  conflict?: string      // 认知冲突标注
}

interface Model {
  name: string
  provider: string
  description: string
}

interface APIConfig {
  provider: 'minimax' | 'openai' | 'anthropic' | 'mock'
  apiKey: string
  baseUrl: string
  model: string
}

interface SolveResult {
  task_id: string
  consensus: string
  alternatives: string[]
  agents_info: { mbti_type: string; name: string }[]
  confidence: number
  full_summary: string
  dimension_analysis: Record<string, string>
  viewpoint_divergence: number  // 观点分歧度 (0-1, 越高表示分歧越大)
  krippendorff_alpha: number    // Krippendorff α系数 (1表示完全一致)
}

const DEFAULT_CONFIG: APIConfig = {
  provider: 'minimax',
  apiKey: 'sk-cp-ZCwysUdUK1bPpueFdYe-yr97Q9-mRKFFNP8q1WYNcsIBrR_eT9nuHWEz0EKPPy3s7xAjvUvUCxcf_jShb6XCd674oPOZm5aantIXyAn4Fexo-qTYyNhvxkc',
  baseUrl: 'http://10.68.46.180:31943',
  model: 'MiniMax-M2.7',
}

function App() {
  // State
  const [query, setQuery] = useState('')
  const [selectedCombination, setSelectedCombination] = useState('')
  const [combinations, setCombinations] = useState<Combination[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [selectedModel, setSelectedModel] = useState('MiniMax-M2.7')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<SolveResult | null>(null)
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState<'solve' | 'agents' | 'about'>('solve')
  const [showSettings, setShowSettings] = useState(false)
  const [apiConfig, setApiConfig] = useState<APIConfig>(() => {
    const saved = localStorage.getItem('mbti_api_config')
    return saved ? JSON.parse(saved) : DEFAULT_CONFIG
  })

  // Load combinations and models on mount
  useEffect(() => {
    axios.get(`${API_BASE}/combinations`).then(res => {
      setCombinations(res.data.combinations)
    }).catch(console.error)

    axios.get(`${API_BASE}/models`).then(res => {
      setModels(res.data.models)
    }).catch(console.error)
  }, [])

  // Save config when changed
  useEffect(() => {
    localStorage.setItem('mbti_api_config', JSON.stringify(apiConfig))
  }, [apiConfig])

  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setResult(null)

    try {
      console.log('Sending request:', { query: query.trim(), model: selectedModel, task_type: selectedCombination })
      console.log('API Config:', apiConfig)
      const payload = {
        query: query.trim(),
        task_type: selectedCombination || undefined,
        model: selectedModel,
      }
      console.log('Payload:', JSON.stringify(payload))
      const res = await axios.post<SolveResult>(`${API_BASE}/solve`, payload, {
        headers: {
          'Content-Type': 'application/json',
          'X-API-Config': JSON.stringify(apiConfig),
        }
      })
      console.log('Response:', res.data)
      setResult(res.data)
    } catch (err: any) {
      // 解析错误信息，提供更友好的提示
      let errorMessage = '请求失败'
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        if (err.message.includes('Network Error') || err.message.includes('net::')) {
          errorMessage = '网络连接失败，请检查网络或API配置（SSL证书错误可能需要IT部门支持）'
        } else if (err.message.includes('timeout')) {
          errorMessage = '请求超时，请稍后重试或检查API配置'
        } else {
          errorMessage = err.message
        }
      }
      setError(errorMessage)
      console.error('Request error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Handle config change
  const handleConfigChange = (key: keyof APIConfig, value: string) => {
    setApiConfig(prev => ({ ...prev, [key]: value }))
  }

  // Render
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-indigo-600 text-white py-6">
        <div className="max-w-6xl mx-auto px-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">MBTI 多智能体辩论系统</h1>
            <p className="text-indigo-200 mt-2">让16种人格Agent帮您思考问题</p>
          </div>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="px-4 py-2 bg-indigo-700 hover:bg-indigo-800 rounded-lg font-medium transition-colors"
          >
            {showSettings ? '关闭设置' : 'API设置'}
          </button>
        </div>
      </header>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-yellow-50 border-b border-yellow-200">
          <div className="max-w-6xl mx-auto px-4 py-4">
            <h3 className="font-bold text-gray-800 mb-3">API配置</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Provider
                </label>
                <select
                  value={apiConfig.provider}
                  onChange={e => handleConfigChange('provider', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                >
                  <option value="minimax">MiniMax</option>
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="mock">Mock (测试)</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="password"
                  value={apiConfig.apiKey}
                  onChange={e => handleConfigChange('apiKey', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="sk-..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Base URL
                </label>
                <input
                  type="text"
                  value={apiConfig.baseUrl}
                  onChange={e => handleConfigChange('baseUrl', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="http://..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  当前模型
                </label>
                <input
                  type="text"
                  value={apiConfig.model}
                  onChange={e => handleConfigChange('model', e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg"
                  placeholder="MiniMax-M2.7"
                />
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              配置将保存在浏览器本地。Provider切换时，API URL会自动变化。
            </p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex gap-6 py-3">
            <button
              onClick={() => setActiveTab('solve')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'solve'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              解决问题
            </button>
            <button
              onClick={() => setActiveTab('agents')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'agents'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Agent列表
            </button>
            <button
              onClick={() => setActiveTab('about')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'about'
                  ? 'bg-indigo-100 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              关于项目
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {activeTab === 'solve' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Input Form */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">输入您的问题</h2>
              <form onSubmit={handleSubmit}>
                <textarea
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="例如：我应该选择考研还是工作？"
                  className="w-full h-32 p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    选择问题类型（系统将自动推荐最优Agent组合）
                  </label>
                  <select
                    value={selectedCombination}
                    onChange={e => setSelectedCombination(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    <option value="">自动检测（推荐）</option>
                    {combinations.map(c => (
                      <option key={c.id} value={c.id}>
                        {c.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* 推荐组合展示 */}
                {selectedCombination && combinations.find(c => c.id === selectedCombination) && (
                  <div className="mt-4 p-4 bg-indigo-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-indigo-700">推荐Agent组合：</span>
                      {combinations.find(c => c.id === selectedCombination)?.agents.map(agent => (
                        <span key={agent} className="px-2 py-1 bg-indigo-600 text-white rounded text-sm font-bold">
                          {agent}
                        </span>
                      ))}
                    </div>
                    <div className="text-sm text-indigo-600">
                      <span className="font-medium">认知冲突维度：</span>
                      {combinations.find(c => c.id === selectedCombination)?.conflict}
                    </div>
                    <div className="text-sm text-indigo-600 mt-1">
                      <span className="font-medium">各Agent角色：</span>
                      {combinations.find(c => c.id === selectedCombination)?.dimensions?.join(' / ')}
                    </div>
                  </div>
                )}

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    选择AI模型
                  </label>
                  <select
                    value={selectedModel}
                    onChange={e => setSelectedModel(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  >
                    {models.map(m => (
                      <option key={m.name} value={m.name}>
                        {m.name}
                      </option>
                    ))}
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="mt-4 w-full bg-indigo-600 text-white py-3 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      思考中...
                    </span>
                  ) : (
                    '开始辩论'
                  )}
                </button>
              </form>

              {error && (
                <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg">
                  {error}
                </div>
              )}
            </div>

            {/* Result Display */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-bold text-gray-800 mb-4">辩论结果</h2>

              {result ? (
                <div className="space-y-4">
                  {/* Agents */}
                  <div className="flex gap-2 flex-wrap">
                    {result.agents_info.map(agent => (
                      <span
                        key={agent.mbti_type}
                        className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium"
                      >
                        {agent.mbti_type}
                      </span>
                    ))}
                  </div>

                  {/* Evaluation Metrics */}
                  <div className="flex gap-2 flex-wrap">
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
                      置信度: {result.confidence.toFixed(2)}
                    </span>
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                      观点分歧度: {result.viewpoint_divergence.toFixed(2)}
                    </span>
                    <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                      Krippendorff α: {result.krippendorff_alpha.toFixed(2)}
                    </span>
                  </div>

                  {/* Consensus */}
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">共识结论</h3>
                    <div className="p-4 bg-gray-50 rounded-lg text-gray-800 whitespace-pre-wrap">
                      {result.consensus}
                    </div>
                  </div>

                  {/* Alternatives */}
                  {result.alternatives.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-700 mb-2">备选观点</h3>
                      <ul className="space-y-2">
                        {result.alternatives.map((alt, i) => (
                          <li key={i} className="p-3 bg-yellow-50 rounded-lg text-gray-700">
                            {alt}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Dimension Analysis */}
                  <div>
                    <h3 className="font-medium text-gray-700 mb-2">维度分析</h3>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(result.dimension_analysis).map(([dim, analysis]) => (
                        <div key={dim} className="p-2 bg-blue-50 rounded text-sm">
                          <span className="font-medium text-blue-700">{dim}:</span> {analysis}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center h-64 text-gray-400">
                  <p>提交问题后，这里将显示辩论结果</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'agents' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">16种MBTI Agent类型</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { type: 'INTJ', name: '战略家', desc: '逻辑驱动，擅长长远规划' },
                { type: 'INTP', name: '逻辑学家', desc: '抽象分析，追求理论完备' },
                { type: 'ENTJ', name: '指挥官', desc: '果断决策，驱动行动' },
                { type: 'ENTP', name: '辩论家', desc: '辩证思维，挑战现状' },
                { type: 'INFJ', name: '提倡者', desc: '共情洞察，关注价值' },
                { type: 'INFP', name: '调停者', desc: '理想主义，忠于内心' },
                { type: 'ENFJ', name: '主人公', desc: '激励人心，推动共识' },
                { type: 'ENFP', name: '竞选者', desc: '热情创造，探索可能' },
                { type: 'ISTJ', name: '检查员', desc: '务实可靠，遵循规则' },
                { type: 'ISFJ', name: '守护者', desc: '忠诚奉献，关注细节' },
                { type: 'ESTJ', name: '执行者', desc: '高效务实，维护秩序' },
                { type: 'ESFJ', name: '提供者', desc: '热情助人，构建和谐' },
                { type: 'ISTP', name: '手艺人', desc: '灵活务实，擅长技术' },
                { type: 'ISFP', name: '艺术家', desc: '敏感审美，珍惜自由' },
                { type: 'ESTP', name: '企业家', desc: '冒险实践，把握当下' },
                { type: 'ESFP', name: '表演者', desc: '热情社交，享受生活' },
              ].map(agent => (
                <div key={agent.type} className="p-4 border border-gray-200 rounded-lg hover:border-indigo-300 transition-colors">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 bg-indigo-600 text-white rounded text-sm font-bold">
                      {agent.type}
                    </span>
                    <span className="font-medium text-gray-800">{agent.name}</span>
                  </div>
                  <p className="text-sm text-gray-600">{agent.desc}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'about' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">关于项目</h2>
            <div className="prose max-w-none">
              <h3 className="text-lg font-semibold">核心思想</h3>
              <p className="text-gray-600">
                MBTI多智能体辩论系统将16种MBTI人格量表投射到LLM Agent的行为空间，
                让同一底座LLM通过不同Prompt模板扮演16种"性格Agent"，
                由一组性格互补的Agent互相辩论、投票、仲裁，输出带人格多样性的答案。
              </p>

              <h3 className="text-lg font-semibold mt-4">核心创新</h3>
              <ul className="list-disc list-inside text-gray-600">
                <li>同质Agent的群智 ≠ 真群智 — 3个一样的GPT-4互相challenge，本质还是GPT-4</li>
                <li>异质Agent才能产生认知冲突 — INTJ（战略）+ ESFP（共情）+ ISTJ（务实）三个角色天然存在视角差异</li>
              </ul>

              <h3 className="text-lg font-semibold mt-4">技术架构</h3>
              <ul className="list-disc list-inside text-gray-600">
                <li>16套MBTI性格Prompt模板（性格描述 + Few-shot + 知识约束）</li>
                <li>智能组合选择器（根据任务类型自动选择Agent组合）</li>
                <li>多轮辩论机制（初始陈述 → 交叉挑战 → 置信度更新 → 投票）</li>
                <li>多维仲裁器（T-F/N-S/J-P冲突自动分诊处理）</li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App