import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function DocumentViewer() {
    const { '*': docPath } = useParams();
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadDocument();
    }, [docPath]);

    const loadDocument = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`/api/docs/${docPath}`);
            if (!response.ok) {
                throw new Error(`Document not found: ${docPath}`);
            }
            const data = await response.json();
            setContent(data.content);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Simple markdown to HTML converter
    const renderMarkdown = (md) => {
        if (!md) return '';

        let html = md
            // Escape HTML
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            // Headers
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Unordered lists
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            // Ordered lists  
            .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
            // Blockquotes
            .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
            // Horizontal rules
            .replace(/^---$/gm, '<hr />')
            // Line breaks (paragraphs)
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n/g, '<br />');

        // Wrap list items
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
        // Clean up multiple ul tags
        html = html.replace(/<\/ul>\s*<ul>/g, '');

        return `<p>${html}</p>`;
    };

    const getDocumentTitle = () => {
        if (!docPath) return 'Document';
        const fileName = docPath.split('/').pop()?.replace('.md', '') || 'Document';
        return fileName
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    if (loading) {
        return (
            <div className="document-viewer">
                <div className="document-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading document...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="document-viewer">
                <div className="document-error">
                    <div className="error-icon">📄</div>
                    <h2>Document Not Found</h2>
                    <p>{error}</p>
                    <Link to="/" className="back-link">← Back to Checklist</Link>
                </div>
            </div>
        );
    }

    return (
        <div className="document-viewer">
            <div className="document-header">
                <Link to="/" className="back-link">← Back to Checklist</Link>
                <h1>{getDocumentTitle()}</h1>
                <div className="document-path">{docPath}</div>
            </div>

            <div className="document-content">
                <div
                    className="markdown-body"
                    dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
                />
            </div>
        </div>
    );
}

export default DocumentViewer;
