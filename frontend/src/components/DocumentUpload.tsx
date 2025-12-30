import React, { useState, useCallback } from 'react'
import { Upload, FileText, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { JobQueue, QueueItemData } from '@shared/components/JobQueue'

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

interface DocumentUploadProps {
    disabled?: boolean
}

export default function DocumentUpload({ disabled = false }: DocumentUploadProps) {
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
        const interval = setInterval(fetchDocuments, 3000)
        return () => clearInterval(interval)
    }, [fetchDocuments])

    const handleUpload = async (file: File) => {
        if (disabled) return
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
        if (disabled) return
        setDragActive(false)
        const file = e.dataTransfer.files[0]
        if (file) handleUpload(file)
    }, [targetLang, outputFormat, disabled])

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

    const queueItems: QueueItemData[] = documents.map(doc => ({
        id: doc.id,
        title: doc.filename,
        subtitle: `${doc.file_type.toUpperCase()} • ${formatBytes(doc.file_size_bytes)}`,
        status: doc.status,
        progress: doc.progress,
        createdAt: doc.created_at,
        error: doc.error || undefined,
        icon: FileText
    }))

    return (
        <div className="max-w-6xl mx-auto p-6">
            <h2 className="text-2xl font-display font-bold text-oatmeal-900 dark:text-oatmeal-50 mb-6">
                Document Translation
            </h2>

            {/* Upload Zone */}
            <div
                className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all ${
                    disabled
                        ? 'border-oatmeal-200 dark:border-oatmeal-800 bg-oatmeal-50 dark:bg-oatmeal-900 opacity-60 cursor-not-allowed'
                        : dragActive
                        ? 'border-accent bg-accent/5'
                        : 'border-oatmeal-300 dark:border-oatmeal-700 hover:border-accent'
                }`}
                onDragOver={(e) => { e.preventDefault(); if (!disabled) setDragActive(true) }}
                onDragLeave={() => setDragActive(false)}
                onDrop={handleDrop}
            >
                <Upload className={`w-12 h-12 mx-auto mb-4 ${disabled ? 'text-oatmeal-300' : 'text-oatmeal-400'}`} />
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
                        disabled={disabled}
                        className="px-3 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
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
                        disabled={disabled}
                        className="px-3 py-2 rounded-lg border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <option value="json">JSON</option>
                        <option value="csv">CSV</option>
                    </select>
                </div>

                <label className={`inline-flex items-center gap-2 px-4 py-2 bg-accent text-white rounded-lg transition-colors ${
                    disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:bg-accent/90'
                }`}>
                    <Upload className="w-4 h-4" />
                    {isUploading ? 'Uploading...' : 'Browse Files'}
                    <input
                        type="file"
                        className="hidden"
                        accept=".pdf,.docx,.doc,.txt,.md,.csv"
                        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
                        disabled={disabled || isUploading}
                    />
                </label>
            </div>

            {/* Documents List */}
            <div className="mt-8 space-y-4">
                <h3 className="text-lg font-semibold text-oatmeal-800 dark:text-oatmeal-200">
                    Recent Documents
                </h3>

                <JobQueue 
                    items={queueItems}
                    onDelete={handleDelete}
                    renderActions={(item) => item.status === 'completed' ? (
                         <button
                            onClick={(e) => {
                                e.stopPropagation()
                                handleDownload(item.id)
                            }}
                            className="p-2 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-700 rounded-lg transition-colors"
                            title="Download"
                        >
                            <Download className="w-5 h-5 text-accent" />
                        </button>
                    ) : null}
                />
            </div>
        </div>
    )
}
