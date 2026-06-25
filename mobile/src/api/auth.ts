/**
 * Authentication API
 */
import {apiClient} from './client';
import {User, ApiResponse} from '../types';
import * as Keychain from 'react-native-keychain';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  full_name: string;
  specialty?: string;
  institution?: string;
}

export const authApi = {
  /**
   * Login user
   */
  login: async (credentials: LoginCredentials) => {
    const response = await apiClient.post<ApiResponse<{user: User; access_token: string}>>(
      '/users/login',
      credentials,
    );
    
    // Store token securely
    if (response.data?.access_token) {
      await Keychain.setGenericPassword(
        credentials.email,
        response.data.access_token,
      );
    }
    
    return response.data;
  },

  /**
   * Register new user
   */
  register: async (data: RegisterData) => {
    const response = await apiClient.post<ApiResponse<{user: User; access_token: string}>>(
      '/users/register',
      data,
    );
    
    // Store token securely
    if (response.data?.access_token) {
      await Keychain.setGenericPassword(
        data.email,
        response.data.access_token,
      );
    }
    
    return response.data;
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      await apiClient.post('/users/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear stored credentials
      await Keychain.resetGenericPassword();
    }
  },

  /**
   * Get current user profile
   */
  getProfile: async () => {
    return await apiClient.get<User>('/users/me');
  },

  /**
   * Check if token is valid
   */
  validateToken: async () => {
    try {
      await apiClient.get('/users/me');
      return true;
    } catch (error) {
      return false;
    }
  },
};
