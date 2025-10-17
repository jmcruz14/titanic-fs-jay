import { PaginatedResponse, Filters } from '@/types/passenger';
import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:8000';

export function useApi<T>(endpoint: string) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}${endpoint}`)
      .then(res => res.json())
      .then(setData)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [endpoint]);

  return { data, loading, error };
}

export function usePaginatedApi(page: number, pageSize: number, filters: Filters) {
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          page_size: pageSize.toString(),
        });

        if (filters.survived !== undefined) params.append('survived', filters.survived.toString());
        if (filters.sex) params.append('sex', filters.sex);
        if (filters.pclass) params.append('pclass', filters.pclass.toString());
        if (filters.sibsp !== undefined) params.append('sibsp', filters.sibsp.toString());
        if (filters.parch !== undefined) params.append('parch', filters.parch.toString());
        if (filters.embarked) params.append('embarked', filters.embarked);

        const response = await fetch(`${API_BASE}/passengers?${params}`);
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [page, pageSize, JSON.stringify(filters)]);

  return { data, loading, error };
}
