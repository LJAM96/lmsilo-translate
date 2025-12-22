/**
 * API client for Translate backend
 */

const API_BASE = '/api'

export const api = {
    // Models
    async getModels() {
        const res = await fetch(`${API_BASE}/models`)
        if (!res.ok) throw new Error('Failed to fetch models')
        return res.json()
    },

    async getBuiltinModels() {
        const res = await fetch(`${API_BASE}/models/builtin`)
        if (!res.ok) throw new Error('Failed to fetch builtin models')
        return res.json()
    },

    async registerModel(model: {
        name: string
        engine: string
        source: string
        model_id: string
        info?: Record<string, unknown>
    }) {
        const res = await fetch(`${API_BASE}/models`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ...model,
                model_type: 'translation',
            }),
        })
        if (!res.ok) {
            const error = await res.json()
            throw new Error(error.detail || 'Failed to register model')
        }
        return res.json()
    },

    async downloadModel(id: string, force = false) {
        const res = await fetch(`${API_BASE}/models/${id}/download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model_id: id, force }),
        })
        if (!res.ok) throw new Error('Failed to start download')
        return res.json()
    },

    async setDefaultModel(id: string) {
        const res = await fetch(`${API_BASE}/models/${id}/set-default`, {
            method: 'POST',
        })
        if (!res.ok) throw new Error('Failed to set default')
        return res.json()
    },

    async deleteModel(id: string) {
        const res = await fetch(`${API_BASE}/models/${id}`, {
            method: 'DELETE',
        })
        if (!res.ok) throw new Error('Failed to delete model')
    },

    // Translation
    async translate(text: string, sourceLang: string | null, targetLang: string) {
        const res = await fetch(`${API_BASE}/translate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text,
                source_lang: sourceLang,
                target_lang: targetLang,
            }),
        })
        if (!res.ok) {
            const error = await res.json()
            throw new Error(error.detail || 'Translation failed')
        }
        return res.json()
    },

    async getLanguages() {
        const res = await fetch(`${API_BASE}/languages`)
        if (!res.ok) throw new Error('Failed to fetch languages')
        return res.json()
    },
}
