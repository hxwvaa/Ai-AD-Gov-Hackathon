// src/services/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000/api'
});

export interface OpinionRequest {
  title: string;
  description: string;
  department: string;
  attachments: File[];
}

export interface AnalysisResult {
  topics: string[];
  summary: string;
  keyPoints: string[];
  suggestedDepartments: string[];
  relatedOpinions: any[];
}

export const apiService = {
  async submitOpinionRequest(request: OpinionRequest) {
    const formData = new FormData();
    formData.append('title', request.title);
    formData.append('description', request.description);
    formData.append('department', request.department);
    
    request.attachments.forEach(file => {
      formData.append('attachments', file);
    });

    const response = await api.post<AnalysisResult>('/opinion-requests', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  async getOpinions() {
    const response = await api.get('/opinions');
    return response.data;
  },

  async getOpinionById(id: string) {
    const response = await api.get(`/opinions/${id}`);
    return response.data;
  },

  async getDepartments() {
    const response = await api.get('/departments');
    return response.data;
  }
};

// src/hooks/useOpinionRequest.ts
import { useState } from 'react';
import { apiService, OpinionRequest, AnalysisResult } from '../services/api';

export const useOpinionRequest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  const submitRequest = async (request: OpinionRequest) => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.submitOpinionRequest(request);
      setResult(response);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    submitRequest,
    loading,
    error,
    result
  };
};