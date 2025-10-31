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
      
      // Check for rate limit errors
      const errorMessage = error instanceof Error ? error.message : String(error);
      if (errorMessage.includes('429') || errorMessage.includes('rate limit') || errorMessage.includes('quota')) {
        throw new Error('Rate limit exceeded. The chat service is temporarily unavailable. Please try again in a few moments.');
      }
      
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
  getErrorMessage(error?: Error): ChatMessage {
    const errorMsg = error?.message || '';
    
    if (errorMsg.includes('rate limit') || errorMsg.includes('quota') || errorMsg.includes('429')) {
      return {
        role: 'assistant',
        content: "⚠️ I'm experiencing high demand right now. Please wait a moment and try again, or feel free to browse our products manually."
      };
    }
    
    return {
      role: 'assistant',
      content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment, or feel free to browse our products manually."
    };
  }
}

export const chatbotService = new ChatbotService();
export default chatbotService;
