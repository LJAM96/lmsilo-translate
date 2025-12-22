import { useQuery } from '@tanstack/react-query'
import { Download, Filter, RefreshCw, FileText, Clock, User, Server } from 'lucide-react'
import { useState } from 'react'

interface AuditLog {
    id: string
    service: string
    action: string
    timestamp: string
    username: string | null
    ip_address: string | null
    job_id: string | null
    file_name: string | null
    file_hash: string | null
    file_size_bytes: number | null
    processing_time_ms: number | null
    model_used: string | null
    status: string | null
    error_message: string | null
}

export default function AuditLogViewer() {
    const [filters, setFilters] = useState({
        service: '',
        username: '',
        fromDate: '',
        toDate: '',
    })
    const [showFilters, setShowFilters] = useState(false)

    const { data: logs, isLoading, refetch } = useQuery<AuditLog[]>({
        queryKey: ['audit-logs', filters],
        queryFn: async () => {
            const params = new URLSearchParams()
            if (filters.service) params.append('service', filters.service)
            if (filters.username) params.append('username', filters.username)
            if (filters.fromDate) params.append('from_date', filters.fromDate)
            if (filters.toDate) params.append('to_date', filters.toDate)
            const res = await fetch(`/api/audit?${params}`)
            return res.json()
        },
        refetchInterval: 10000,
    })

    const handleExport = async (format: 'csv' | 'json') => {
        const params = new URLSearchParams()
        params.append('format', format)
        if (filters.service) params.append('service', filters.service)
        if (filters.username) params.append('username', filters.username)
        if (filters.fromDate) params.append('from_date', filters.fromDate)
        if (filters.toDate) params.append('to_date', filters.toDate)

        const res = await fetch(`/api/audit/export?${params}`)
        const blob = await res.blob()
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `audit_logs.${format}`
        a.click()
    }

    const formatTime = (ms: number | null) => {
        if (!ms) return '-'
        if (ms < 1000) return `${ms}ms`
        return `${(ms / 1000).toFixed(1)}s`
    }

    const formatSize = (bytes: number | null) => {
        if (!bytes) return '-'
        if (bytes < 1024) return `${bytes}B`
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
        return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
    }

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                    Audit Log
                </h2>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowFilters(!showFilters)}
                        className="px-3 py-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 flex items-center gap-2"
                    >
                        <Filter className="w-4 h-4" />
                        Filters
                    </button>
                    <button
                        onClick={() => refetch()}
                        className="px-3 py-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => handleExport('csv')}
                        className="px-3 py-2 rounded-lg bg-accent text-white hover:bg-accent/90 flex items-center gap-2"
                    >
                        <Download className="w-4 h-4" />
                        Export CSV
                    </button>
                </div>
            </div>

            {showFilters && (
                <div className="mb-6 p-4 bg-oatmeal-100 dark:bg-oatmeal-800 rounded-xl">
                    <div className="grid grid-cols-4 gap-4">
                        <div>
                            <label className="block text-sm mb-1 text-oatmeal-600 dark:text-oatmeal-300">Service</label>
                            <select
                                value={filters.service}
                                onChange={(e) => setFilters({ ...filters, service: e.target.value })}
                                className="w-full px-3 py-2 rounded-lg bg-white dark:bg-oatmeal-900 border border-oatmeal-200 dark:border-oatmeal-700"
                            >
                                <option value="">All</option>
                                <option value="locate">Locate</option>
                                <option value="transcribe">Transcribe</option>
                                <option value="translate">Translate</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm mb-1 text-oatmeal-600 dark:text-oatmeal-300">Username</label>
                            <input
                                type="text"
                                value={filters.username}
                                onChange={(e) => setFilters({ ...filters, username: e.target.value })}
                                placeholder="Filter by user"
                                className="w-full px-3 py-2 rounded-lg bg-white dark:bg-oatmeal-900 border border-oatmeal-200 dark:border-oatmeal-700"
                            />
                        </div>
                        <div>
                            <label className="block text-sm mb-1 text-oatmeal-600 dark:text-oatmeal-300">From Date</label>
                            <input
                                type="datetime-local"
                                value={filters.fromDate}
                                onChange={(e) => setFilters({ ...filters, fromDate: e.target.value })}
                                className="w-full px-3 py-2 rounded-lg bg-white dark:bg-oatmeal-900 border border-oatmeal-200 dark:border-oatmeal-700"
                            />
                        </div>
                        <div>
                            <label className="block text-sm mb-1 text-oatmeal-600 dark:text-oatmeal-300">To Date</label>
                            <input
                                type="datetime-local"
                                value={filters.toDate}
                                onChange={(e) => setFilters({ ...filters, toDate: e.target.value })}
                                className="w-full px-3 py-2 rounded-lg bg-white dark:bg-oatmeal-900 border border-oatmeal-200 dark:border-oatmeal-700"
                            />
                        </div>
                    </div>
                </div>
            )}

            {isLoading ? (
                <div className="text-center py-12 text-oatmeal-500">Loading...</div>
            ) : (
                <div className="bg-white dark:bg-oatmeal-900 rounded-xl overflow-hidden border border-oatmeal-200 dark:border-oatmeal-700">
                    <table className="w-full text-sm">
                        <thead className="bg-oatmeal-50 dark:bg-oatmeal-800">
                            <tr>
                                <th className="px-4 py-3 text-left font-medium">Time</th>
                                <th className="px-4 py-3 text-left font-medium">Service</th>
                                <th className="px-4 py-3 text-left font-medium">Action</th>
                                <th className="px-4 py-3 text-left font-medium">User</th>
                                <th className="px-4 py-3 text-left font-medium">File</th>
                                <th className="px-4 py-3 text-left font-medium">Duration</th>
                                <th className="px-4 py-3 text-left font-medium">Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-oatmeal-100 dark:divide-oatmeal-800">
                            {logs?.map((log) => (
                                <tr key={log.id} className="hover:bg-oatmeal-50 dark:hover:bg-oatmeal-800/50">
                                    <td className="px-4 py-3 text-oatmeal-600 dark:text-oatmeal-400">
                                        {new Date(log.timestamp).toLocaleString()}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="px-2 py-1 rounded-full text-xs bg-accent/10 text-accent">
                                            {log.service}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">{log.action}</td>
                                    <td className="px-4 py-3 flex items-center gap-1">
                                        <User className="w-3 h-3 text-oatmeal-400" />
                                        {log.username || log.ip_address || '-'}
                                    </td>
                                    <td className="px-4 py-3">
                                        {log.file_name ? (
                                            <span className="flex items-center gap-1">
                                                <FileText className="w-3 h-3 text-oatmeal-400" />
                                                {log.file_name}
                                                <span className="text-oatmeal-400 text-xs">
                                                    ({formatSize(log.file_size_bytes)})
                                                </span>
                                            </span>
                                        ) : '-'}
                                    </td>
                                    <td className="px-4 py-3 flex items-center gap-1">
                                        <Clock className="w-3 h-3 text-oatmeal-400" />
                                        {formatTime(log.processing_time_ms)}
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`px-2 py-1 rounded-full text-xs ${log.status === 'success'
                                                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                                                : log.status === 'failed'
                                                    ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                                                    : 'bg-oatmeal-100 text-oatmeal-600'
                                            }`}>
                                            {log.status || '-'}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {(!logs || logs.length === 0) && (
                        <div className="text-center py-12 text-oatmeal-500">
                            No audit logs found
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
