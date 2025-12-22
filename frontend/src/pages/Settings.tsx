import { useState } from 'react'
import { Settings as SettingsIcon, FileText, Info } from 'lucide-react'
import AuditLogViewer from '../components/AuditLogViewer'

type SettingsTab = 'audit' | 'about'

export default function Settings() {
    const [activeTab, setActiveTab] = useState<SettingsTab>('audit')

    return (
        <div className="max-w-6xl mx-auto">
            {/* Tab Navigation */}
            <div className="flex items-center gap-4 px-6 pt-6 border-b border-oatmeal-200 dark:border-oatmeal-700">
                <button
                    onClick={() => setActiveTab('audit')}
                    className={`pb-3 px-2 font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'audit'
                            ? 'border-accent text-accent'
                            : 'border-transparent text-oatmeal-500 hover:text-oatmeal-700'
                        }`}
                >
                    <FileText className="w-4 h-4" />
                    Audit Log
                </button>
                <button
                    onClick={() => setActiveTab('about')}
                    className={`pb-3 px-2 font-medium flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'about'
                            ? 'border-accent text-accent'
                            : 'border-transparent text-oatmeal-500 hover:text-oatmeal-700'
                        }`}
                >
                    <Info className="w-4 h-4" />
                    About
                </button>
            </div>

            {/* Tab Content */}
            {activeTab === 'audit' && <AuditLogViewer />}
            {activeTab === 'about' && (
                <div className="p-6">
                    <div className="bg-white dark:bg-oatmeal-900 rounded-xl p-6 border border-oatmeal-200 dark:border-oatmeal-700">
                        <h3 className="text-xl font-display font-semibold mb-4">LMSilo Translate</h3>
                        <p className="text-oatmeal-600 dark:text-oatmeal-400 mb-4">
                            AI-powered translation using Meta's NLLB-200 model supporting 200+ languages.
                        </p>
                        <div className="text-sm text-oatmeal-500">
                            <p>Part of the LMSilo Local AI Suite</p>
                            <p className="mt-1">Version 1.0.0</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
