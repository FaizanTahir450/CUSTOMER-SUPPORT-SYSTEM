import { authToken } from './client';

const USER_KEY = 'lumina_user';

export interface CurrentUser {
  id: string;
  email: string;
  name?: string;
  role?: string;
  created_at: string;
}

export const authUtils = {
  setUser: (user: CurrentUser) => {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  getUser: (): CurrentUser | null => {
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  isAuthenticated: (): boolean => {
    return !!authToken.get() && !!localStorage.getItem(USER_KEY);
  },

  logout: () => {
    authToken.clear();
    localStorage.removeItem(USER_KEY);
  },
};
