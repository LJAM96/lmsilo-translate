import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Download, Trash2, Check, Loader2, Plus, AlertCircle, Languages } from 'lucide-react'
import toast from 'react-hot-toast'
import { api } from '../lib/api'
import { useState } from 'react'
import AddModelModal from '../components/AddModelModal'

interface Model {
    id: string
    name: string
    engine: string
    is_default: boolean
    is_downloaded: boolean
    download_progress?: number
    info: {
        size_mb?: number
        description?: string
        recommended_vram_gb?: number
        num_languages?: number
    }
}

export default function Models() {
    const [showAddModal, setShowAddModal] = useState(false)
    const [deletingId, setDeletingId] = useState<string | null>(null)
    const queryClient = useQueryClient()

    const { data: models, isLoading } = useQuery<Model[]>({
        queryKey: ['models'],
        queryFn: () => api.getModels(),
        refetchInterval: (query) => {
            // Refetch more often if any model is downloading
            const hasDownloading = query.state.data?.some(
                (m: Model) => m.download_progress !== null && m.download_progress !== undefined && m.download_progress < 100
            )
            return hasDownloading ? 2000 : 10000
        },
    })

    const handleDownload = async (id: string) => {
        try {
            await api.downloadModel(id)
            toast.success('Download started')
            queryClient.invalidateQueries({ queryKey: ['models'] })
        } catch (e) {
            toast.error(e instanceof Error ? e.message : 'Download failed')
        }
    }

    const handleSetDefault = async (id: string) => {
        try {
            await api.setDefaultModel(id)
            toast.success('Default model updated')
            queryClient.invalidateQueries({ queryKey: ['models'] })
        } catch (e) {
            toast.error(e instanceof Error ? e.message : 'Failed to set default')
        }
    }

    const handleDelete = async (id: string) => {
        setDeletingId(id)
        try {
            await api.deleteModel(id)
            toast.success('Model deleted')
            queryClient.invalidateQueries({ queryKey: ['models'] })
        } catch (e) {
            toast.error(e instanceof Error ? e.message : 'Delete failed')
        } finally {
            setDeletingId(null)
        }
    }

    return (
        <div className="min-h-screen bg-oatmeal-50 dark:bg-oatmeal-950">
            <div className="max-w-4xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div>
                        <h1 className="text-2xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                            Translation Models
                        </h1>
                        <p className="text-oatmeal-600 dark:text-oatmeal-400 mt-1">
                            Manage NLLB and other translation models
                        </p>
                    </div>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Plus className="w-4 h-4" />
                        Add Model
                    </button>
                </div>

                {/* Models List */}
                {isLoading ? (
                    <div className="text-center py-12">
                        <Loader2 className="w-8 h-8 animate-spin mx-auto text-accent" />
                        <p className="mt-2 text-oatmeal-500">Loading models...</p>
                    </div>
                ) : models && models.length > 0 ? (
                    <div className="space-y-3">
                        {models.map((model) => (
                            <div
                                key={model.id}
                                className="card flex items-center gap-4"
                            >
                                {/* Icon */}
                                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                                    <Languages className="w-5 h-5 text-accent" />
                                </div>

                                {/* Info */}
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2">
                                        <span className="font-medium text-oatmeal-900 dark:text-oatmeal-100">
                                            {model.name}
                                        </span>
                                        <span className="text-xs text-oatmeal-500 bg-oatmeal-100 dark:bg-oatmeal-800 px-1.5 py-0.5 rounded">
                                            {model.engine}
                                        </span>
                                        {model.is_default && (
                                            <span className="text-xs text-accent bg-accent/10 px-1.5 py-0.5 rounded">
                                                Default
                                            </span>
                                        )}
                                    </div>
                                    <div className="text-sm text-oatmeal-500 mt-0.5">
                                        {model.info?.description || 'No description'}
                                    </div>

                                    {/* Download progress */}
                                    {model.download_progress !== null &&
                                        model.download_progress !== undefined &&
                                        model.download_progress < 100 && (
                                            <div className="mt-2">
                                                <div className="h-1.5 bg-oatmeal-200 dark:bg-oatmeal-700 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-accent rounded-full transition-all"
                                                        style={{ width: `${model.download_progress}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs text-oatmeal-500 mt-1">
                                                    Downloading... {Math.round(model.download_progress)}%
                                                </span>
                                            </div>
                                        )}
                                </div>

                                {/* Stats */}
                                <div className="flex items-center gap-4 text-sm text-oatmeal-500 flex-shrink-0">
                                    {model.info?.size_mb && (
                                        <span>{(model.info.size_mb / 1024).toFixed(1)} GB</span>
                                    )}
                                    {model.info?.num_languages && (
                                        <span>{model.info.num_languages} langs</span>
                                    )}
                                </div>

                                {/* Actions */}
                                <div className="flex items-center gap-2 flex-shrink-0">
                                    {!model.is_downloaded ? (
                                        <button
                                            onClick={() => handleDownload(model.id)}
                                            className="p-2 rounded-lg bg-accent text-white hover:bg-accent/90 transition-colors"
                                            title="Download"
                                        >
                                            <Download className="w-4 h-4" />
                                        </button>
                                    ) : (
                                        !model.is_default && (
                                            <button
                                                onClick={() => handleSetDefault(model.id)}
                                                className="p-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 transition-colors"
                                                title="Set as default"
                                            >
                                                <Check className="w-4 h-4 text-oatmeal-600 dark:text-oatmeal-300" />
                                            </button>
                                        )
                                    )}
                                    <button
                                        onClick={() => handleDelete(model.id)}
                                        disabled={deletingId === model.id}
                                        className="p-2 rounded-lg bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                                        title="Delete"
                                    >
                                        {deletingId === model.id ? (
                                            <Loader2 className="w-4 h-4 animate-spin text-red-500" />
                                        ) : (
                                            <Trash2 className="w-4 h-4 text-red-500" />
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-16 card">
                        <AlertCircle className="w-12 h-12 text-oatmeal-300 dark:text-oatmeal-600 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-oatmeal-700 dark:text-oatmeal-300">
                            No models registered
                        </h3>
                        <p className="text-oatmeal-500 mt-1 mb-6">
                            Add a translation model to get started
                        </p>
                        <button
                            onClick={() => setShowAddModal(true)}
                            className="btn-primary"
                        >
                            Add Your First Model
                        </button>
                    </div>
                )}
            </div>

            {/* Add Model Modal */}
            <AddModelModal
                isOpen={showAddModal}
                onClose={() => setShowAddModal(false)}
            />
        </div>
    )
}
