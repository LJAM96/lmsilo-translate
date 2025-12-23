import React, { useState, useCallback } from 'react'
import { Upload, FileText, CheckCircle, XCircle, Loader2, Download, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

interface DocumentJob {
    id: string
    filename: string
    file_type: string
    file_size_bytes: number
    status: string
    progress: number
    total_blocks: number
    processed_blocks: number
    languages_found: Record<string, number>
    blocks_skipped: number
    blocks_translated: number
    target_lang: string
    error: string | null
    created_at: string
    completed_at: string | null
    processing_time_ms: number | null
}

const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    extracting: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    detecting: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    translating: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200',
    completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}

export default function DocumentUpload() {
    const [documents, setDocuments] = useState<DocumentJob[]>([])
    const [isUploading, setIsUploading] = useState(false)
    const [targetLang, setTargetLang] = useState('eng_Latn')
    const [outputFormat, setOutputFormat] = useState('json')
    const [dragActive, setDragActive] = useState(false)

    const fetchDocuments = useCallback(async () => {
        try {
            const res = await fetch('/api/documents')
            if (res.ok) {
                const data = await res.json()
                setDocuments(data)
            }
        } catch (error) {
            console.error('Failed to fetch documents:', error)
        }
    }, [])

    React.useEffect(() => {
        fetchDocuments()
        const interval = setInterval(fetchDocuments, 3000) // Poll for updates
        return () => clearInterval(interval)
    }, [fetchDocuments])

    const handleUpload = async (file: File) => {
        setIsUploading(true)
        const formData = new FormData()
        formData.append('file', file)
        formData.append('target_lang', targetLang)
        formData.append('output_format', outputFormat)

        try {
            const res = await fetch('/api/documents', {
                method: 'POST',
                body: formData,
            })

            if (res.ok) {
                toast.success(`Uploaded ${file.name}`)
                fetchDocuments()
            } else {
                const error = await res.json()
                toast.error(error.detail || 'Upload failed')
            }
        } catch (error) {
            toast.error('Upload failed')
        } finally {
            setIsUploading(false)
        }
    }

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setDragActive(false)
        const file = e.dataTransfer.files[0]
        if (file) handleUpload(file)
    }, [targetLang, outputFormat])

    const handleDelete = async (id: string) => {
        try {
            const res = await fetch(`/api/documents/${id}`, { method: 'DELETE' })
            if (res.ok) {
                toast.success('Document deleted')
                fetchDocuments()
            }
        } catch (error) {
            toast.error('Delete failed')
        }
    }

    const handleDownload = (id: string) => {
        window.open(`/api/documents/${id}/download`, '_blank')
    }

    const formatBytes = (bytes: number) => {
        if (bytes < 1024) return `${bytes} B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
        return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
    }

    return (
        <div className="max-w-6xl mx-auto p-6">
            <h2 className="text-2xl font-display font-bold text-oatmeal-900 dark:text-oatmeal-50 mb-6">
                Document Translation
            </h2>

            {/* Upload Zone */}
            <div
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${dragActive
                        ? 'border-accent bg-accent/5'
                        : 'border-oatmeal-300 dark:border-oatmeal-700 hover:border-accent'
                    }`}
                onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
            >
                <Upload className="w-12 h-12 mx-auto mb-4 text-oatmeal-400" />
                <p className="text-lg font-medium text-oatmeal-700 dark:text-oatmeal-300 mb-2">
                    Drag & drop a document here
                </p>
                <p className="text-sm text-oatmeal-500 mb-4">
                    PDF, DOCX, DOC, TXT, MD, CSV
                </p>

                <div className="flex items-center justify-center gap-4 mb-4">
                    <select
                        value={targetLang}
                        onChange={(e) => setTargetLang(e.target.value)}
                        className="px-3 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-sm"
                    >
                        <option value="eng_Latn">English</option>
                        <option value="spa_Latn">Spanish</option>
                        <option value="fra_Latn">French</option>
                        <option value="deu_Latn">German</option>
                        <option value="zho_Hans">Chinese (Simplified)</option>
                    </select>

                    <select
                        value={outputFormat}
                        onChange={(e) => setOutputFormat(e.target.value)}
                        className="px-3 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-sm"
                    >
                        <option value="json">JSON</option>
                        <option value="csv">CSV</option>
                    </select>
                </div>

                <label className="inline-flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg cursor-pointer hover:bg-accent/90 transition-colors">
                    <Upload className="w-4 h-4" />
                    {isUploading ? 'Uploading...' : 'Browse Files'}
                    <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.doc,.txt,.md,.csv"
                        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
                        disabled={isUploading}
                    />
                </label>
            </div>

            {/* Documents List */}
            <div className="mt-8 space-y-4">
                <h3 className="text-lg font-semibold text-oatmeal-800 dark:text-oatmeal-200">
                    Recent Documents
                </h3>

                {documents.length === 0 ? (
                    <p className="text-oatmeal-500 text-center py-8">No documents yet</p>
                ) : (
                    documents.map((doc) => (
                        <div
                            key={doc.id}
                            className="bg-white dark:bg-oatmeal-800 rounded-xl p-4 shadow-sm border border-oatmeal-200 dark:border-oatmeal-700"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <FileText className="w-8 h-8 text-oatmeal-400" />
                                    <div>
                                        <p className="font-medium text-oatmeal-900 dark:text-oatmeal-100">
                                            {doc.filename}
                                        </p>
                                        <p className="text-sm text-oatmeal-500">
                                            {doc.file_type.toUpperCase()} • {formatBytes(doc.file_size_bytes)}
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[doc.status]}`}>
                                        {doc.status}
                                    </span>

                                    {doc.status === 'completed' && (
                                        <button
                                            onClick={() => handleDownload(doc.id)}
                                            className="p-2 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-700 rounded-lg transition-colors"
                                        >
                                            <Download className="w-5 h-5 text-accent" />
                                        </button>
                                    )}

                                    <button
                                        onClick={() => handleDelete(doc.id)}
                                        className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                    >
                                        <Trash2 className="w-5 h-5 text-red-500" />
                                    </button>
                                </div>
                            </div>

                            {/* Progress Bar */}
                            {['extracting', 'detecting', 'translating'].includes(doc.status) && (
                                <div className="mt-3">
                                    <div className="flex items-center justify-between text-sm text-oatmeal-500 mb-1">
                                        <span>{doc.processed_blocks} / {doc.total_blocks} blocks</span>
                                        <span>{doc.progress}%</span>
                                    </div>
                                    <div className="h-2 bg-oatmeal-100 dark:bg-oatmeal-700 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-accent transition-all duration-300"
                                            style={{ width: `${doc.progress}%` }}
                                        />
                                    </div>
                                </div>
                            )}

                            {/* Stats for completed */}
                            {doc.status === 'completed' && (
                                <div className="mt-3 flex items-center gap-4 text-sm text-oatmeal-500">
                                    <span className="flex items-center gap-1">
                                        <CheckCircle className="w-4 h-4 text-green-500" />
                                        {doc.blocks_translated} translated
                                    </span>
                                    <span>
                                        {doc.blocks_skipped} English (skipped)
                                    </span>
                                    {doc.processing_time_ms && (
                                        <span>
                                            {(doc.processing_time_ms / 1000).toFixed(1)}s
                                        </span>
                                    )}
                                </div>
                            )}

                            {/* Error Display */}
                            {doc.status === 'failed' && doc.error && (
                                <div className="mt-3 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg text-sm text-red-600 dark:text-red-400">
                                    {doc.error}
                                </div>
                            )}
                        </div>
                    ))
                )}
            </div>
        </div>
    )
}
