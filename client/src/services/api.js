const API_BASE = '/api';

/**
 * API client for LexAI backend
 */
export const api = {
    /**
     * Search cases with hybrid search
     */
    async search(query, options = {}) {
        const response = await fetch(`${API_BASE}/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                search_type: options.searchType || 'hybrid',
                jurisdictions: options.jurisdictions || null,
                court_levels: options.courtLevels || null,
                page: options.page || 1,
                page_size: options.pageSize || 10
            })
        });
        if (!response.ok) throw new Error('Search failed');
        return response.json();
    },

    /**
     * Get all cases
     */
    async getCases(options = {}) {
        const params = new URLSearchParams();
        if (options.limit) params.set('limit', options.limit);
        if (options.offset) params.set('offset', options.offset);
        if (options.status) params.set('status', options.status);

        const response = await fetch(`${API_BASE}/cases?${params}`);
        if (!response.ok) throw new Error('Failed to fetch cases');
        return response.json();
    },

    /**
     * Get a specific case by ID
     */
    async getCase(caseId) {
        const response = await fetch(`${API_BASE}/cases/${caseId}`);
        if (!response.ok) throw new Error('Case not found');
        return response.json();
    },

    /**
     * Get KeyCite status for a case
     */
    async getKeyCite(caseId) {
        const response = await fetch(`${API_BASE}/cases/${caseId}/keycite`);
        if (!response.ok) throw new Error('KeyCite failed');
        return response.json();
    },

    /**
     * Get citation network for a case
     */
    async getCitationNetwork(caseId, depth = 2) {
        const response = await fetch(`${API_BASE}/cases/${caseId}/citations?depth=${depth}`);
        if (!response.ok) throw new Error('Citations failed');
        return response.json();
    },

    /**
     * Check overruling risks for a case
     */
    async checkRisks(caseId) {
        const response = await fetch(`${API_BASE}/cases/${caseId}/risks`);
        if (!response.ok) throw new Error('Risk check failed');
        return response.json();
    },

    /**
     * Chat with AI assistant
     */
    async chat(message, history = []) {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message,
                conversation_history: history,
                include_sources: true
            })
        });
        if (!response.ok) throw new Error('Chat failed');
        return response.json();
    },

    /**
     * Get chat example questions
     */
    async getChatExamples() {
        const response = await fetch(`${API_BASE}/chat/examples`);
        if (!response.ok) throw new Error('Failed to fetch examples');
        return response.json();
    },

    /**
     * Get dashboard statistics
     */
    async getDashboard() {
        const response = await fetch(`${API_BASE}/analytics/dashboard`);
        if (!response.ok) throw new Error('Dashboard failed');
        return response.json();
    },

    /**
     * Search judges
     */
    async searchJudges(query = '') {
        const response = await fetch(`${API_BASE}/analytics/judges?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Judge search failed');
        return response.json();
    },

    /**
     * Get judge profile
     */
    async getJudge(judgeId) {
        const response = await fetch(`${API_BASE}/analytics/judges/${judgeId}`);
        if (!response.ok) throw new Error('Judge not found');
        return response.json();
    },

    /**
     * Get case timeline
     */
    async getCaseTimeline(caseId) {
        const response = await fetch(`${API_BASE}/analytics/cases/${caseId}/timeline`);
        if (!response.ok) throw new Error('Timeline failed');
        return response.json();
    },

    /**
     * Get authority rankings
     */
    async getAuthorityRanking(topic = null, limit = 10) {
        const params = new URLSearchParams();
        if (topic) params.set('topic', topic);
        params.set('limit', limit);

        const response = await fetch(`${API_BASE}/analytics/authority?${params}`);
        if (!response.ok) throw new Error('Authority ranking failed');
        return response.json();
    },

    /**
     * Get search suggestions
     */
    async getSuggestions(query) {
        const response = await fetch(`${API_BASE}/search/suggestions?query=${encodeURIComponent(query)}`);
        if (!response.ok) throw new Error('Suggestions failed');
        return response.json();
    },

    /**
     * Get legal topics
     */
    async getTopics() {
        const response = await fetch(`${API_BASE}/search/topics`);
        if (!response.ok) throw new Error('Topics failed');
        return response.json();
    }
};

export default api;
