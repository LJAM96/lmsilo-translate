import DocumentUpload from '../components/DocumentUpload'

export default function DocumentsPage() {
    return (
        <div>
            <h2 className="text-2xl font-serif text-surface-800 dark:text-cream-100 mb-6">
                Document Translation
            </h2>
            <DocumentUpload />
        </div>
    )
}
