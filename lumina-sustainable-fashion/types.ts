
export interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  image: string;
  description: string;
}

export interface Message {
  id: string;
  type: 'user' | 'bot';
  text: string;
  timestamp: Date;
  isError?: boolean;
}

export interface Config {
  apiUrl: string;
  userId: string;
  useGemini: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}
