import { useState, useEffect } from 'react'
import { ArrowRightLeft, Copy, Check, Loader2, ChevronDown, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'

interface Language {
    code: string
    name: string
}

export default function TranslatePage() {
    const [sourceText, setSourceText] = useState('')
    const [translatedText, setTranslatedText] = useState('')
    const [sourceLang, setSourceLang] = useState('auto')
    const [targetLang, setTargetLang] = useState('eng_Latn')
    const [languages, setLanguages] = useState<Language[]>([])
    const [isTranslating, setIsTranslating] = useState(false)
    const [copied, setCopied] = useState(false)
    const [detectedLang, setDetectedLang] = useState<string | null>(null)

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

    return (
        <div className="space-y-6">
            {/* Language Selection */}
            <div className="flex items-center justify-center gap-4">
                <div className="flex-1 max-w-xs">
                    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
                        Source Language
                    </label>
                    <div className="relative">
                        <select
                            value={sourceLang}
                            onChange={(e) => setSourceLang(e.target.value)}
                            className="select w-full"
                        >
                            <option value="auto">Auto Detect</option>
                            {languages.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                    </div>
                    {detectedLang && (
                        <p className="mt-1 text-xs text-olive-600 dark:text-olive-400">
                            Detected: {languages.find(l => l.code === detectedLang)?.name || detectedLang}
                        </p>
                    )}
                </div>

                <button
                    onClick={handleSwapLanguages}
                    disabled={sourceLang === 'auto'}
                    className="p-3 mt-6 rounded-xl bg-cream-200 dark:bg-dark-100 hover:bg-cream-300 dark:hover:bg-dark-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                    <ArrowRightLeft className="w-5 h-5 text-surface-600 dark:text-surface-300" />
                </button>

                <div className="flex-1 max-w-xs">
                    <label className="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
                        Target Language
                    </label>
                    <div className="relative">
                        <select
                            value={targetLang}
                            onChange={(e) => setTargetLang(e.target.value)}
                            className="select w-full"
                        >
                            {languages.map((lang) => (
                                <option key={lang.code} value={lang.code}>
                                    {lang.name}
                                </option>
                            ))}
                        </select>
                        <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Text Areas */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Source Text */}
                <div className="card">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-surface-800 dark:text-cream-100">Source Text</h3>
                        <button
                            onClick={handleClear}
                            className="text-sm text-surface-500 hover:text-surface-700 dark:hover:text-surface-300"
                        >
                            Clear
                        </button>
                    </div>
                    <textarea
                        value={sourceText}
                        onChange={(e) => setSourceText(e.target.value)}
                        placeholder="Enter text to translate..."
                        className="input min-h-[200px] resize-none"
                    />
                </div>

                {/* Translated Text */}
                <div className="card">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="font-medium text-surface-800 dark:text-cream-100">Translation</h3>
                        <button
                            onClick={handleCopy}
                            disabled={!translatedText}
                            className="text-sm text-surface-500 hover:text-surface-700 dark:hover:text-surface-300 disabled:opacity-50 flex items-center gap-1"
                        >
                            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            {copied ? 'Copied' : 'Copy'}
                        </button>
                    </div>
                    <div className="input min-h-[200px] whitespace-pre-wrap">
                        {translatedText || <span className="text-surface-400">Translation will appear here...</span>}
                    </div>
                </div>
            </div>

            {/* Translate Button */}
            <div className="flex justify-center">
                <button
                    onClick={handleTranslate}
                    disabled={isTranslating || !sourceText.trim()}
                    className="btn-primary flex items-center gap-2"
                >
                    {isTranslating ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Translating...
                        </>
                    ) : (
                        <>
                            <RefreshCw className="w-5 h-5" />
                            Translate
                        </>
                    )}
                </button>
            </div>

            {/* Info */}
            <div className="text-center text-sm text-surface-500 dark:text-surface-400 max-w-2xl mx-auto">
                <p>
                    This translation service is powered by Meta's NLLB-200 (No Language Left Behind) model,
                    supporting over 200 languages. The model runs locally for privacy and can handle
                    low-resource languages that are often underserved by commercial translation services.
                </p>
            </div>
        </div>
    )
}
