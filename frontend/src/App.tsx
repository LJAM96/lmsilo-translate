import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/Layout'
import TranslatePage from './pages/Translate'
import DocumentsPage from './pages/Documents'
import ModelsPage from './pages/Models'
import SettingsPage from './pages/Settings'

export default function App() {
    return (
        <>
            <Toaster position="top-right" />
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Layout />}>
                        <Route index element={<TranslatePage />} />
                        <Route path="documents" element={<DocumentsPage />} />
                        <Route path="models" element={<ModelsPage />} />
                        <Route path="settings" element={<SettingsPage />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </>
    )
}
