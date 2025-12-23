import { useState, useEffect } from 'react'
import { Languages, ArrowRightLeft, Copy, Check, Moon, Sun, Loader2, ChevronDown, RefreshCw, Settings } from 'lucide-react'
import toast, { Toaster } from 'react-hot-toast'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

interface Language {
    code: string
    name: string
}

function TranslateApp() {
    const [darkMode, setDarkMode] = useState(() => {
        if (typeof window !== 'undefined') {
            return localStorage.getItem('theme') === 'dark' ||
                (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
        }
        return false
    })

    const [currentPage, setCurrentPage] = useState<'translate' | 'models' | 'jobs' | 'settings'>('translate')
    const [sourceText, setSourceText] = useState('')
    const [translatedText, setTranslatedText] = useState('')
    const [sourceLang, setSourceLang] = useState('auto')
    const [targetLang, setTargetLang] = useState('eng_Latn')
    const [languages, setLanguages] = useState<Language[]>([])
    const [isTranslating, setIsTranslating] = useState(false)
    const [copied, setCopied] = useState(false)
    const [detectedLang, setDetectedLang] = useState<string | null>(null)

    useEffect(() => {
        if (darkMode) {
            document.documentElement.classList.add('dark')
            localStorage.setItem('theme', 'dark')
        } else {
            document.documentElement.classList.remove('dark')
            localStorage.setItem('theme', 'light')
        }
    }, [darkMode])

    useEffect(() => {
        fetchLanguages()
    }, [])

    const fetchLanguages = async () => {
        try {
            const res = await fetch('/api/languages')
            if (res.ok) {
                const data = await res.json()
                setLanguages(data.languages || data || [])
            }
        } catch (error) {
            console.error('Failed to fetch languages:', error)
        }
    }

    const handleTranslate = async () => {
        if (!sourceText.trim()) {
            toast.error('Please enter text to translate')
            return
        }

        setIsTranslating(true)
        setDetectedLang(null)

        try {
            const res = await fetch('/api/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: sourceText,
                    source_lang: sourceLang === 'auto' ? null : sourceLang,
                    target_lang: targetLang,
                }),
            })

            if (!res.ok) {
                const error = await res.json()
                throw new Error(error.detail || 'Translation failed')
            }

            const data = await res.json()
            setTranslatedText(data.translation || data.translated_text)
            if (data.source_lang) {
                setDetectedLang(data.source_lang)
            }
            toast.success('Translation complete')
        } catch (error) {
            toast.error(error instanceof Error ? error.message : 'Translation failed')
        } finally {
            setIsTranslating(false)
        }
    }

    const handleSwapLanguages = () => {
        if (sourceLang === 'auto') return
        setSourceLang(targetLang)
        setTargetLang(sourceLang)
        setSourceText(translatedText)
        setTranslatedText(sourceText)
    }

    const handleCopy = async () => {
        if (!translatedText) return
        await navigator.clipboard.writeText(translatedText)
        setCopied(true)
        toast.success('Copied to clipboard')
        setTimeout(() => setCopied(false), 2000)
    }

    const handleClear = () => {
        setSourceText('')
        setTranslatedText('')
        setDetectedLang(null)
    }

    // Dynamically import Models page
    if (currentPage === 'models') {
        const Models = require('./pages/Models').default
        return (
            <div className="min-h-screen bg-oatmeal-50 dark:bg-oatmeal-950 transition-colors duration-300">
                <Toaster position="top-right" />
                <header className="sticky top-0 z-50 backdrop-blur-md bg-oatmeal-50/80 dark:bg-oatmeal-950/80 border-b border-oatmeal-200 dark:border-oatmeal-800">
                    <div className="max-w-6xl mx-auto px-4 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-accent/10 rounded-xl">
                                        <Languages className="w-6 h-6 text-accent" />
                                    </div>
                                    <h1 className="text-xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                                        Translate
                                    </h1>
                                </div>
                                <nav className="flex items-center gap-1">
                                    <button
                                        onClick={() => setCurrentPage('translate')}
                                        className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800"
                                    >
                                        Translate
                                    </button>
                                    <button
                                        onClick={() => setCurrentPage('models')}
                                        className={`px-3 py-1.5 text-sm rounded-lg ${currentPage === 'models' ? 'bg-accent/10 text-accent' : 'text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800'}`}
                                    >
                                        Models
                                    </button>
                                    <button
                                        onClick={() => setCurrentPage('jobs')}
                                        className={`px-3 py-1.5 text-sm rounded-lg ${currentPage === 'jobs' ? 'bg-accent/10 text-accent' : 'text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800'}`}
                                    >
                                        Jobs
                                    </button>
                                    <button
                                        onClick={() => setCurrentPage('settings')}
                                        className={`px-3 py-1.5 text-sm rounded-lg ${currentPage === 'settings' ? 'bg-accent/10 text-accent' : 'text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800'}`}
                                    >
                                        Settings
                                    </button>
                                </nav>
                            </div>
                            <button
                                onClick={() => setDarkMode(!darkMode)}
                                className="p-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 transition-colors"
                            >
                                {darkMode ? <Sun className="w-5 h-5 text-oatmeal-300" /> : <Moon className="w-5 h-5 text-oatmeal-600" />}
                            </button>
                        </div>
                    </div>
                </header>
                <Models />
            </div>
        )
    }

    // Render Jobs page
    if (currentPage === 'jobs') {
        const JobList = require('./components/JobList').default
        return (
            <div className="min-h-screen bg-oatmeal-50 dark:bg-oatmeal-950 transition-colors duration-300">
                <Toaster position="top-right" />
                <header className="sticky top-0 z-50 backdrop-blur-md bg-oatmeal-50/80 dark:bg-oatmeal-950/80 border-b border-oatmeal-200 dark:border-oatmeal-800">
                    <div className="max-w-6xl mx-auto px-4 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-accent/10 rounded-xl">
                                        <Languages className="w-6 h-6 text-accent" />
                                    </div>
                                    <h1 className="text-xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                                        Translate
                                    </h1>
                                </div>
                                <nav className="flex items-center gap-1">
                                    <button onClick={() => setCurrentPage('translate')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Translate</button>
                                    <button onClick={() => setCurrentPage('models')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Models</button>
                                    <button onClick={() => setCurrentPage('jobs')} className="px-3 py-1.5 text-sm rounded-lg bg-accent/10 text-accent">Jobs</button>
                                    <button onClick={() => setCurrentPage('settings')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Settings</button>
                                </nav>
                            </div>
                            <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 transition-colors">
                                {darkMode ? <Sun className="w-5 h-5 text-oatmeal-300" /> : <Moon className="w-5 h-5 text-oatmeal-600" />}
                            </button>
                        </div>
                    </div>
                </header>
                <JobList />
            </div>
        )
    }

    // Render Settings page
    if (currentPage === 'settings') {
        const Settings = require('./pages/Settings').default
        return (
            <div className="min-h-screen bg-oatmeal-50 dark:bg-oatmeal-950 transition-colors duration-300">
                <Toaster position="top-right" />
                <header className="sticky top-0 z-50 backdrop-blur-md bg-oatmeal-50/80 dark:bg-oatmeal-950/80 border-b border-oatmeal-200 dark:border-oatmeal-800">
                    <div className="max-w-6xl mx-auto px-4 py-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-6">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-accent/10 rounded-xl">
                                        <Languages className="w-6 h-6 text-accent" />
                                    </div>
                                    <h1 className="text-xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                                        Translate
                                    </h1>
                                </div>
                                <nav className="flex items-center gap-1">
                                    <button onClick={() => setCurrentPage('translate')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Translate</button>
                                    <button onClick={() => setCurrentPage('models')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Models</button>
                                    <button onClick={() => setCurrentPage('jobs')} className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800">Jobs</button>
                                    <button onClick={() => setCurrentPage('settings')} className="px-3 py-1.5 text-sm rounded-lg bg-accent/10 text-accent">Settings</button>
                                </nav>
                            </div>
                            <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 transition-colors">
                                {darkMode ? <Sun className="w-5 h-5 text-oatmeal-300" /> : <Moon className="w-5 h-5 text-oatmeal-600" />}
                            </button>
                        </div>
                    </div>
                </header>
                <Settings />
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-oatmeal-50 dark:bg-oatmeal-950 transition-colors duration-300">
            <Toaster
                position="top-right"
                toastOptions={{
                    className: 'dark:bg-oatmeal-800 dark:text-oatmeal-100',
                }}
            />

            {/* Header */}
            <header className="sticky top-0 z-50 backdrop-blur-md bg-oatmeal-50/80 dark:bg-oatmeal-950/80 border-b border-oatmeal-200 dark:border-oatmeal-800">
                <div className="max-w-6xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-accent/10 rounded-xl">
                                    <Languages className="w-6 h-6 text-accent" />
                                </div>
                                <div>
                                    <h1 className="text-xl font-display font-semibold text-oatmeal-900 dark:text-oatmeal-50">
                                        Translate
                                    </h1>
                                    <p className="text-sm text-oatmeal-600 dark:text-oatmeal-400">
                                        AI-Powered Translation
                                    </p>
                                </div>
                            </div>
                            <nav className="flex items-center gap-1">
                                <button
                                    onClick={() => setCurrentPage('translate')}
                                    className="px-3 py-1.5 text-sm rounded-lg bg-accent/10 text-accent"
                                >
                                    Translate
                                </button>
                                <button
                                    onClick={() => setCurrentPage('models')}
                                    className="px-3 py-1.5 text-sm rounded-lg text-oatmeal-600 dark:text-oatmeal-300 hover:bg-oatmeal-100 dark:hover:bg-oatmeal-800 flex items-center gap-1"
                                >
                                    <Settings className="w-4 h-4" />
                                    Models
                                </button>
                            </nav>
                        </div>

                        <button
                            onClick={() => setDarkMode(!darkMode)}
                            className="p-2 rounded-lg bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 transition-colors"
                            aria-label="Toggle theme"
                        >
                            {darkMode ? (
                                <Sun className="w-5 h-5 text-oatmeal-600 dark:text-oatmeal-300" />
                            ) : (
                                <Moon className="w-5 h-5 text-oatmeal-600 dark:text-oatmeal-300" />
                            )}
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-6xl mx-auto px-4 py-8">
                {/* Language Selection */}
                <div className="flex items-center justify-center gap-4 mb-6">
                    <div className="flex-1 max-w-xs">
                        <label className="block text-sm font-medium text-oatmeal-700 dark:text-oatmeal-300 mb-2">
                            Source Language
                        </label>
                        <div className="relative">
                            <select
                                value={sourceLang}
                                onChange={(e) => setSourceLang(e.target.value)}
                                className="w-full appearance-none px-4 py-3 pr-10 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-oatmeal-900 dark:text-oatmeal-100 focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                            >
                                <option value="auto">Auto-detect</option>
                                {languages.map((lang) => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-oatmeal-400 pointer-events-none" />
                        </div>
                        {detectedLang && sourceLang === 'auto' && (
                            <p className="mt-1 text-sm text-accent">
                                Detected: {languages.find(l => l.code === detectedLang)?.name || detectedLang}
                            </p>
                        )}
                    </div>

                    <button
                        onClick={handleSwapLanguages}
                        disabled={sourceLang === 'auto'}
                        className="p-3 mt-6 rounded-xl bg-oatmeal-100 dark:bg-oatmeal-800 hover:bg-oatmeal-200 dark:hover:bg-oatmeal-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        aria-label="Swap languages"
                    >
                        <ArrowRightLeft className="w-5 h-5 text-oatmeal-600 dark:text-oatmeal-300" />
                    </button>

                    <div className="flex-1 max-w-xs">
                        <label className="block text-sm font-medium text-oatmeal-700 dark:text-oatmeal-300 mb-2">
                            Target Language
                        </label>
                        <div className="relative">
                            <select
                                value={targetLang}
                                onChange={(e) => setTargetLang(e.target.value)}
                                className="w-full appearance-none px-4 py-3 pr-10 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700 bg-white dark:bg-oatmeal-800 text-oatmeal-900 dark:text-oatmeal-100 focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                            >
                                {languages.map((lang) => (
                                    <option key={lang.code} value={lang.code}>
                                        {lang.name}
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 text-oatmeal-400 pointer-events-none" />
                        </div>
                    </div>
                </div>

                {/* Translation Panels */}
                <div className="grid md:grid-cols-2 gap-6">
                    {/* Source Panel */}
                    <div className="card">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-medium text-oatmeal-900 dark:text-oatmeal-100">
                                Source Text
                            </h2>
                            <button
                                onClick={handleClear}
                                disabled={!sourceText}
                                className="text-sm text-oatmeal-500 hover:text-oatmeal-700 dark:hover:text-oatmeal-300 disabled:opacity-50 transition-colors"
                            >
                                Clear
                            </button>
                        </div>
                        <textarea
                            value={sourceText}
                            onChange={(e) => setSourceText(e.target.value)}
                            placeholder="Enter text to translate..."
                            className="w-full h-64 p-4 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700 bg-oatmeal-50 dark:bg-oatmeal-800/50 text-oatmeal-900 dark:text-oatmeal-100 placeholder:text-oatmeal-400 resize-none focus:outline-none focus:ring-2 focus:ring-accent/50 transition-all"
                        />
                        <div className="flex items-center justify-between mt-4">
                            <span className="text-sm text-oatmeal-500">
                                {sourceText.length} characters
                            </span>
                            <button
                                onClick={handleTranslate}
                                disabled={isTranslating || !sourceText.trim()}
                                className="btn-primary flex items-center gap-2"
                            >
                                {isTranslating ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Translating...
                                    </>
                                ) : (
                                    <>
                                        <RefreshCw className="w-4 h-4" />
                                        Translate
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Target Panel */}
                    <div className="card">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="font-medium text-oatmeal-900 dark:text-oatmeal-100">
                                Translation
                            </h2>
                            <button
                                onClick={handleCopy}
                                disabled={!translatedText}
                                className="flex items-center gap-1 text-sm text-oatmeal-500 hover:text-oatmeal-700 dark:hover:text-oatmeal-300 disabled:opacity-50 transition-colors"
                            >
                                {copied ? (
                                    <>
                                        <Check className="w-4 h-4" />
                                        Copied
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-4 h-4" />
                                        Copy
                                    </>
                                )}
                            </button>
                        </div>
                        <div className="w-full h-64 p-4 rounded-xl border border-oatmeal-200 dark:border-oatmeal-700 bg-oatmeal-50 dark:bg-oatmeal-800/50 overflow-auto">
                            {isTranslating ? (
                                <div className="flex items-center justify-center h-full">
                                    <Loader2 className="w-8 h-8 text-accent animate-spin" />
                                </div>
                            ) : translatedText ? (
                                <p className="text-oatmeal-900 dark:text-oatmeal-100 whitespace-pre-wrap">
                                    {translatedText}
                                </p>
                            ) : (
                                <p className="text-oatmeal-400 italic">
                                    Translation will appear here...
                                </p>
                            )}
                        </div>
                        <div className="flex items-center justify-end mt-4">
                            <span className="text-sm text-oatmeal-500">
                                {translatedText.length} characters
                            </span>
                        </div>
                    </div>
                </div>

                {/* Info Section */}
                <div className="mt-8 p-6 rounded-2xl bg-oatmeal-100/50 dark:bg-oatmeal-800/30 border border-oatmeal-200 dark:border-oatmeal-700">
                    <h3 className="font-display text-lg font-semibold text-oatmeal-900 dark:text-oatmeal-100 mb-2">
                        About NLLB-200
                    </h3>
                    <p className="text-oatmeal-600 dark:text-oatmeal-400 text-sm leading-relaxed">
                        This translation service is powered by Meta's NLLB-200 (No Language Left Behind) model,
                        supporting over 200 languages. The model runs locally for privacy and can handle
                        low-resource languages that are often underserved by commercial translation services.
                    </p>
                </div>
            </main>
        </div>
    )
}

export default TranslateApp
