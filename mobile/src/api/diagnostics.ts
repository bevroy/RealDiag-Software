/**
 * Diagnostics API
 */
import {apiClient} from './client';
import {SearchResponse, DiagnosticTree, SymptomSearchParams} from '../types';

export const diagnosticsApi = {
  /**
   * Search symptoms
   */
  searchSymptoms: async (params: SymptomSearchParams) => {
    const queryString = new URLSearchParams({
      q: params.query,
      ...(params.age && {age: params.age.toString()}),
      ...(params.sex && {sex: params.sex}),
      ...(params.family && {family: params.family}),
    }).toString();

    return await apiClient.get<SearchResponse>(`/search/symptoms?${queryString}`);
  },

  /**
   * Get all diagnostic trees
   */
  getAllTrees: async () => {
    return await apiClient.get<{trees: DiagnosticTree[]}>('/diagnostic/trees');
  },

  /**
   * Get specific diagnostic tree
   */
  getTree: async (treeId: string) => {
    return await apiClient.get<DiagnosticTree>(`/diagnostic/trees/${treeId}`);
  },

  /**
   * Get rules by family/specialty
   */
  getRulesByFamily: async (family: string) => {
    return await apiClient.get<{rules: DiagnosticTree[]}>(`/reference/${family}`);
  },

  /**
   * Add to favorites
   */
  addFavorite: async (ruleId: string, notes?: string) => {
    return await apiClient.post('/users/me/favorites', {
      rule_id: ruleId,
      notes,
    });
  },

  /**
   * Get favorites
   */
  getFavorites: async () => {
    return await apiClient.get('/users/me/favorites');
  },

  /**
   * Add to search history
   */
  addToHistory: async (searchData: SymptomSearchParams & {results: any[]}) => {
    return await apiClient.post('/users/me/history', searchData);
  },

  /**
   * Get search history
   */
  getHistory: async () => {
    return await apiClient.get('/users/me/history');
  },
};
