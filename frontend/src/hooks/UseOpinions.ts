// src/hooks/useOpinions.ts
import { useState, useEffect } from 'react';
import { apiService } from '../../services/api';

export interface Opinion {
  id: number;
  title: string;
  department: string;
  status: 'Completed' | 'In Progress' | 'Pending';
  date: string;
  author: string;
  summary: string;
}

export const useOpinions = () => {
  const [opinions, setOpinions] = useState<Opinion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState<string | null>(null);

  useEffect(() => {
    const fetchOpinions = async () => {
      try {
        const data = await apiService.getOpinions();
        setOpinions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch opinions');
      } finally {
        setLoading(false);
      }
    };

    fetchOpinions();
  }, []);

  const filteredOpinions = opinions.filter(opinion => {
    const matchesSearch = opinion.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         opinion.summary.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = !filter || opinion.department === filter;
    return matchesSearch && matchesFilter;
  });

  return {
    opinions: filteredOpinions,
    loading,
    error,
    searchTerm,
    setSearchTerm,
    filter,
    setFilter
  };
};