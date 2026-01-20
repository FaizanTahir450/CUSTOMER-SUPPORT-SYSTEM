
export interface Product {
  id: number;
  name: string;
  price: string;
  imageUrl: string;
  isNew?: boolean;
}

export interface ChatMessage {
  id: number;
  text: string;
  sender: 'user' | 'ai';
}
