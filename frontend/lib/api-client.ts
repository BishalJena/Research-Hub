const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = this.getAuthToken();
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Topics API
  async getTrendingTopics(params?: { discipline?: string; limit?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.discipline) {
      queryParams.append('discipline', params.discipline);
    }
    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    const queryString = queryParams.toString();
    return this.request(`/topics/trending${queryString ? `?${queryString}` : ''}`);
  }

  async searchTopics(query: string) {
    return this.request(`/topics/search?query=${encodeURIComponent(query)}`);
  }

  async getTopicAnalysis(topic: string) {
    return this.request('/topics/analyze', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    });
  }

  // Papers API
  async uploadPaper(formData: FormData) {
    const token = this.getAuthToken();
    const response = await fetch(`${this.baseUrl}/papers/upload`, {
      method: 'POST',
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  }

  async getPapers() {
    return this.request('/papers/');
  }

  async getPaper(paperId: string) {
    return this.request(`/papers/${paperId}`);
  }

  async analyzePaper(paperId: string) {
    return this.request(`/papers/${paperId}/analyze`, {
      method: 'POST',
    });
  }

  // Plagiarism API
  async checkPlagiarism(paperId: string) {
    return this.request('/plagiarism/check', {
      method: 'POST',
      body: JSON.stringify({ paper_id: paperId }),
    });
  }

  async getPlagiarismCheck(checkId: string) {
    return this.request(`/plagiarism/check/${checkId}`);
  }

  // Journals API
  async searchJournals(query: string) {
    return this.request(`/journals/search?query=${encodeURIComponent(query)}`);
  }

  async getRecommendedJournals(paperId: string) {
    return this.request(`/journals/recommend/${paperId}`);
  }

  // Government Priorities API
  async getGovernmentPriorities() {
    return this.request('/government/priorities');
  }

  async alignWithPriorities(paperId: string) {
    return this.request(`/government/align/${paperId}`, {
      method: 'POST',
    });
  }

  // Impact Prediction API
  async predictImpact(paperId: string) {
    return this.request(`/impact/predict/${paperId}`, {
      method: 'POST',
    });
  }

  // Translation API
  async translateText(text: string, targetLang: string) {
    return this.request('/translate', {
      method: 'POST',
      body: JSON.stringify({
        text,
        target_language: targetLang,
      }),
    });
  }

  // Literature Review API
  async getLiteratureReview(topic: string) {
    return this.request('/literature/review', {
      method: 'POST',
      body: JSON.stringify({ topic }),
    });
  }

  async getRecommendedPapers(paperId: string) {
    return this.request(`/literature/recommend/${paperId}`);
  }
}

export const apiClient = new ApiClient();
