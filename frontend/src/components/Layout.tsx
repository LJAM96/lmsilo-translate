import { Outlet, NavLink } from 'react-router-dom'
import { Languages, FileText, Layers, Settings, Moon, Sun } from 'lucide-react'
import { useTheme } from '../lib/theme'

export default function Layout() {
    const { isDark, toggle } = useTheme()

    return (
        <div className="min-h-screen bg-cream-100 dark:bg-dark-400 transition-colors duration-300">
            {/* Header */}
            <header className="bg-white dark:bg-dark-300 border-b border-cream-200 dark:border-dark-100 sticky top-0 z-50 transition-colors duration-300">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        {/* Logo */}
                        <NavLink to="/" className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-olive-600 rounded-xl flex items-center justify-center">
                                <Languages className="w-5 h-5 text-white" />
                            </div>
                            <h1 className="text-2xl font-serif text-surface-800 dark:text-cream-100">Translate</h1>
                        </NavLink>

                        {/* Navigation */}
                        <nav className="flex items-center gap-2">
                            <NavItem to="/" icon={Languages}>Translate</NavItem>
                            <NavItem to="/documents" icon={FileText}>Documents</NavItem>
                            <NavItem to="/models" icon={Layers}>Models</NavItem>
                            <NavItem to="/settings" icon={Settings}>Settings</NavItem>

                            {/* Theme Toggle */}
                            <button
                                onClick={toggle}
                                className="ml-4 p-2 rounded-xl bg-cream-200 dark:bg-dark-100 hover:bg-cream-300 dark:hover:bg-dark-50 transition-colors"
                                aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
                            >
                                {isDark ? (
                                    <Sun className="w-5 h-5 text-cream-400" />
                                ) : (
                                    <Moon className="w-5 h-5 text-surface-600" />
                                )}
                            </button>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Main content */}
            <main className="max-w-7xl mx-auto px-6 py-8">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="border-t border-cream-200 dark:border-dark-100 mt-auto transition-colors">
                <div className="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-surface-500 dark:text-surface-400">
                    <p>AI Translation • Powered by Meta NLLB-200</p>
                </div>
            </footer>
        </div>
    )
}

interface NavItemProps {
    to: string
    icon: React.ElementType
    children: React.ReactNode
}

function NavItem({ to, icon: Icon, children }: NavItemProps) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all duration-200 ${isActive
                    ? 'bg-olive-100 text-olive-800 dark:bg-olive-900/40 dark:text-olive-300'
                    : 'text-surface-600 dark:text-cream-400 hover:bg-cream-200 dark:hover:bg-dark-100 hover:text-surface-800 dark:hover:text-cream-200'
                }`
            }
        >
            <Icon className="w-4 h-4" />
            <span>{children}</span>
        </NavLink>
    )
}
