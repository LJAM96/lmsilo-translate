import { useState, useCallback } from 'react'
import { X, Search, Download, Loader2, ExternalLink, Cpu, Star, Languages } from 'lucide-react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { api } from '../lib/api'

interface AddModelModalProps {
    isOpen: boolean
    onClose: () => void
}

interface BuiltinModel {
    id: string
    name: string
    engine: string
    description: string
    size_mb?: number
    recommended_vram_gb?: number
    num_languages?: number
    hf_id?: string
    popular?: boolean
}

// NLLB models (CT2 converted versions available)
const BUILTIN_MODELS: BuiltinModel[] = [
    {
        id: 'nllb-200-distilled-600M',
        name: 'NLLB-200 Distilled 600M',
        engine: 'nllb-ct2',
        description: 'Fast, good quality for common languages',
        size_mb: 1200,
        recommended_vram_gb: 2,
        num_languages: 200,
        hf_id: 'facebook/nllb-200-distilled-600M',
        popular: true,
    },
    {
        id: 'nllb-200-distilled-1.3B',
        name: 'NLLB-200 Distilled 1.3B',
        engine: 'nllb-ct2',
        description: 'Good balance of speed and quality',
        size_mb: 2600,
        recommended_vram_gb: 4,
        num_languages: 200,
        hf_id: 'facebook/nllb-200-distilled-1.3B',
        popular: true,
    },
    {
        id: 'nllb-200-1.3B',
        name: 'NLLB-200 1.3B',
        engine: 'nllb-ct2',
        description: 'High quality translation',
        size_mb: 5200,
        recommended_vram_gb: 6,
        num_languages: 200,
        hf_id: 'facebook/nllb-200-1.3B',
    },
    {
        id: 'nllb-200-3.3B',
        name: 'NLLB-200 3.3B',
        engine: 'nllb-ct2',
        description: 'Best quality, requires significant resources',
        size_mb: 13000,
        recommended_vram_gb: 12,
        num_languages: 200,
        hf_id: 'facebook/nllb-200-3.3B',
    },
]

export default function AddModelModal({ isOpen, onClose }: AddModelModalProps) {
    const [activeTab, setActiveTab] = useState<'popular' | 'huggingface'>('popular')
    const [searchQuery, setSearchQuery] = useState('')
    const [downloading, setDownloading] = useState<string | null>(null)

    // HuggingFace search
    const [hfSearchQuery, setHfSearchQuery] = useState('')
    const [hfResults, setHfResults] = useState<any[]>([])
    const [hfLoading, setHfLoading] = useState(false)

    const queryClient = useQueryClient()

    const registerMutation = useMutation({
        mutationFn: async (model: BuiltinModel) => {
            return api.registerModel({
                name: model.name,
                engine: model.engine,
                source: 'builtin',
                model_id: model.id,
                info: {
                    description: model.description,
                    size_mb: model.size_mb,
                    recommended_vram_gb: model.recommended_vram_gb,
                    num_languages: model.num_languages,
                },
            })
        },
        onSuccess: (_, model) => {
            toast.success(`${model.name} added`)
            queryClient.invalidateQueries({ queryKey: ['models'] })
        },
        onError: (error) => {
            toast.error(`Failed to add model: ${error}`)
        },
    })

    const handleAddModel = async (model: BuiltinModel) => {
        setDownloading(model.id)
        try {
            await registerMutation.mutateAsync(model)
        } finally {
            setDownloading(null)
        }
    }

    const searchHuggingFace = useCallback(async () => {
        if (!hfSearchQuery.trim()) {
            setHfResults([])
            return
        }

        setHfLoading(true)
        try {
            const response = await fetch(
                `https://huggingface.co/api/models?search=${encodeURIComponent(hfSearchQuery + ' nllb translation')}&limit=15&sort=downloads&direction=-1`
            )

            if (!response.ok) throw new Error('Search failed')

            const models = await response.json()
            // Filter to NLLB-related models
            const filtered = models.filter((m: any) => {
                const id = (m.modelId || m.id).toLowerCase()
                return id.includes('nllb') || id.includes('translation') || id.includes('opus')
            })

            setHfResults(filtered)
        } catch (error) {
            console.error('HuggingFace search error:', error)
            toast.error('Failed to search HuggingFace')
            setHfResults([])
        } finally {
            setHfLoading(false)
        }
    }, [hfSearchQuery])

    const handleAddHFModel = async (hfModel: any) => {
        const modelId = hfModel.modelId || hfModel.id
        setDownloading(modelId)

        try {
            await api.registerModel({
                name: modelId.split('/').pop() || modelId,
                engine: 'nllb-ct2',
                source: 'huggingface',
                model_id: modelId,
                info: {
                    description: `From HuggingFace: ${modelId}`,
                },
            })
            toast.success('Model added')
            queryClient.invalidateQueries({ queryKey: ['models'] })
        } catch (e) {
            toast.error(e instanceof Error ? e.message : 'Failed to add model')
        } finally {
            setDownloading(null)
        }
    }

    const filteredModels = BUILTIN_MODELS.filter((m) =>
        m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        m.description.toLowerCase().includes(searchQuery.toLowerCase())
    )

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/50 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white dark:bg-oatmeal-900 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-oatmeal-200 dark:border-oatmeal-700">
                    <h2 className="text-xl font-display text-oatmeal-900 dark:text-oatmeal-50">
                        Add Translation Model
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-oatmeal-600 dark:text-oatmeal-300" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-oatmeal-200 dark:border-oatmeal-700">
                    {(['popular', 'huggingface'] as const).map((tab) => (
                        <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === tab
                                    ? 'text-accent border-b-2 border-accent'
                                    : 'text-oatmeal-500 hover:text-oatmeal-700'
                                }`}
                        >
                            {tab === 'popular' ? 'NLLB Models' : 'HuggingFace Search'}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="flex-1 overflow-hidden flex flex-col p-6">
                    {activeTab === 'popular' && (
                        <>
                            <div className="relative mb-4">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-oatmeal-400" />
                                <input
                                    type="text"
                                    placeholder="Search models..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-oatmeal-50 dark:bg-oatmeal-800 text-oatmeal-900 dark:text-oatmeal-100"
                                />
                            </div>

                            <div className="flex-1 overflow-y-auto space-y-2">
                                {filteredModels.map((model) => (
                                    <div
                                        key={model.id}
                                        className="p-3 bg-oatmeal-50 dark:bg-oatmeal-800 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div className="w-9 h-9 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                                                <Languages className="w-4 h-4 text-accent" />
                                            </div>

                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-medium text-oatmeal-800 dark:text-oatmeal-200 text-sm">
                                                        {model.name}
                                                    </span>
                                                    {model.popular && (
                                                        <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                                                    )}
                                                </div>
                                                <div className="text-xs text-oatmeal-500 mt-0.5">
                                                    {model.description}
                                                </div>
                                            </div>

                                            <div className="flex items-center gap-3 text-xs text-oatmeal-500 flex-shrink-0">
                                                {model.size_mb && (
                                                    <span>{(model.size_mb / 1024).toFixed(1)}GB</span>
                                                )}
                                                {model.recommended_vram_gb && (
                                                    <span className="flex items-center gap-0.5">
                                                        <Cpu className="w-3 h-3" />
                                                        {model.recommended_vram_gb}GB
                                                    </span>
                                                )}
                                            </div>

                                            <button
                                                onClick={() => handleAddModel(model)}
                                                disabled={downloading !== null}
                                                className={`px-3 py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 ${downloading === model.id
                                                        ? 'bg-accent/20 text-accent'
                                                        : 'bg-accent hover:bg-accent/90 text-white'
                                                    }`}
                                            >
                                                {downloading === model.id ? (
                                                    <Loader2 className="w-3 h-3 animate-spin" />
                                                ) : (
                                                    <Download className="w-3 h-3" />
                                                )}
                                                Add
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {activeTab === 'huggingface' && (
                        <>
                            <div className="flex gap-2 mb-4">
                                <div className="relative flex-1">
                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-oatmeal-400" />
                                    <input
                                        type="text"
                                        placeholder="Search HuggingFace for translation models..."
                                        value={hfSearchQuery}
                                        onChange={(e) => setHfSearchQuery(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && searchHuggingFace()}
                                        className="w-full pl-10 pr-4 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-oatmeal-50 dark:bg-oatmeal-800"
                                    />
                                </div>
                                <button
                                    onClick={searchHuggingFace}
                                    disabled={hfLoading || !hfSearchQuery.trim()}
                                    className="px-4 py-2 bg-accent hover:bg-accent/90 disabled:bg-oatmeal-400 text-white text-sm rounded-lg transition-colors"
                                >
                                    {hfLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Search'}
                                </button>
                            </div>

                            <div className="flex-1 overflow-y-auto space-y-2">
                                {hfResults.length > 0 ? (
                                    hfResults.map((model) => {
                                        const modelId = model.modelId || model.id
                                        return (
                                            <div
                                                key={modelId}
                                                className="p-3 bg-oatmeal-50 dark:bg-oatmeal-800 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700"
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="flex-1 min-w-0">
                                                        <span className="font-medium text-oatmeal-800 dark:text-oatmeal-200 text-sm truncate block">
                                                            {modelId}
                                                        </span>
                                                        <div className="flex items-center gap-3 text-xs text-oatmeal-500 mt-0.5">
                                                            <span>↓ {formatNumber(model.downloads)} downloads</span>
                                                            <span>♥ {formatNumber(model.likes)} likes</span>
                                                        </div>
                                                    </div>

                                                    <a
                                                        href={`https://huggingface.co/${modelId}`}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="p-1.5 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 rounded-lg transition-colors"
                                                    >
                                                        <ExternalLink className="w-4 h-4 text-oatmeal-500" />
                                                    </a>

                                                    <button
                                                        onClick={() => handleAddHFModel(model)}
                                                        disabled={downloading !== null}
                                                        className="px-3 py-1.5 text-xs font-medium rounded-lg transition-colors flex items-center gap-1.5 bg-accent hover:bg-accent/90 text-white"
                                                    >
                                                        {downloading === modelId ? (
                                                            <Loader2 className="w-3 h-3 animate-spin" />
                                                        ) : (
                                                            <Download className="w-3 h-3" />
                                                        )}
                                                        Add
                                                    </button>
                                                </div>
                                            </div>
                                        )
                                    })
                                ) : hfSearchQuery && !hfLoading ? (
                                    <div className="text-center py-8 text-oatmeal-500">
                                        No models found. Try a different search.
                                    </div>
                                ) : (
                                    <div className="text-center py-8 text-oatmeal-500">
                                        <ExternalLink className="w-10 h-10 mx-auto mb-3 opacity-50" />
                                        <p>Search HuggingFace for translation models</p>
                                        <p className="text-xs mt-1">Try: "nllb", "opus", "m2m100"</p>
                                    </div>
                                )}
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

function formatNumber(num: number): string {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return String(num)
}
