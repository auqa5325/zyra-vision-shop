import { apiClient } from './api';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  messages: ChatMessage[];
  user_id?: string;
}

export interface ProductSuggestion {
  product_id: string;
  name: string;
  price: number;
  discount_percent?: number;
  image_url?: string;
  reason: string;
}

export interface ChatResponse {
  message: string;
  suggestions?: string[];
  products?: ProductSuggestion[];
}

class ChatbotService {
  /**
   * Send message to Gemini-powered chatbot
   */
  async sendMessage(messages: ChatMessage[], userId?: string): Promise<ChatResponse> {
    try {
      const response = await apiClient.post<ChatResponse>('/api/chatbot/chat', {
        messages,
        user_id: userId
      });
      
      return response;
    } catch (error) {
      console.error('❌ [CHATBOT] API error:', error);
      throw new Error('Failed to get response from chatbot');
    }
  }

  /**
   * Check if chatbot service is healthy
   */
  async checkHealth(): Promise<boolean> {
    try {
      const response = await apiClient.get('/api/chatbot/health') as { status: string };
      return response.status === 'healthy';
    } catch (error) {
      console.error('❌ [CHATBOT] Health check failed:', error);
      return false;
    }
  }

  /**
   * Get initial greeting message
   */
  getInitialMessage(): ChatMessage {
    return {
      role: 'assistant',
      content: "Hi! I'm Zyra, your AI shopping assistant powered by Gemini. How can I help you find the perfect product today?"
    };
  }

  /**
   * Get error message for when chatbot is unavailable
   */
  getErrorMessage(): ChatMessage {
    return {
      role: 'assistant',
      content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment, or feel free to browse our products manually."
    };
  }
}

export const chatbotService = new ChatbotService();
export default chatbotService;
