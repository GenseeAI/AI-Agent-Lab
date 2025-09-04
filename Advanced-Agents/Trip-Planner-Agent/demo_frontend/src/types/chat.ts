export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

export interface ChatExchange {
  id: string;
  userMessage: ChatMessage;
  aiMessage: ChatMessage;
}

export interface ChatSession {
  id: string;
  name: string;
  messages: ChatMessage[]; // For standalone messages (like initial AI greeting)
  exchanges: ChatExchange[]; // For user-AI conversation pairs
  createdAt: Date;
  updatedAt: Date;
}

export interface ItineraryChats {
  itineraryId: string;
  sessions: ChatSession[];
  activeSessionId?: string | null;
} 