import { useState, useEffect } from 'react';
import { ChatMessage, ChatSession, ItineraryChats, ChatExchange } from '@/types/chat';

const STORAGE_KEY = 'Gensee-Trip-sessions';

// Helper function to truncate text
const truncateText = (text: string, maxLength: number = 50): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

export const useChatSessions = (itineraryId: string | null) => {
  const [itineraryChats, setItineraryChats] = useState<ItineraryChats | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load chat sessions from sessionStorage on component mount or itinerary change
  useEffect(() => {
    if (!itineraryId) {
      setItineraryChats(null);
      setIsLoaded(true);
      return;
    }

    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const allChats: ItineraryChats[] = JSON.parse(stored);
        const existingChats = allChats.find(chat => chat.itineraryId === itineraryId);
        
        if (existingChats) {
          // Convert dates back to Date objects and filter out empty sessions
          const processedChats: ItineraryChats = {
            ...existingChats,
            sessions: existingChats.sessions
              .map(session => ({
                ...session,
                createdAt: new Date(session.createdAt),
                updatedAt: new Date(session.updatedAt),
                messages: (session.messages || []).map(message => ({
                  ...message,
                  timestamp: new Date(message.timestamp)
                })),
                exchanges: (session.exchanges || []).map(exchange => ({
                  ...exchange,
                  userMessage: {
                    ...exchange.userMessage,
                    timestamp: new Date(exchange.userMessage.timestamp)
                  },
                  aiMessage: {
                    ...exchange.aiMessage,
                    timestamp: new Date(exchange.aiMessage.timestamp)
                  }
                }))
              })),
          };

          // If no valid sessions remain, set activeSessionId to null
          if (processedChats.sessions.length === 0) {
            processedChats.activeSessionId = null;
          } else if (!processedChats.activeSessionId || 
                     !processedChats.sessions.find(s => s.id === processedChats.activeSessionId)) {
            // If active session was removed, set to first available session
            processedChats.activeSessionId = processedChats.sessions[0].id;
          }

          setItineraryChats(processedChats);
          
          // Save the cleaned up sessions back to storage
          saveToSessionStorage(processedChats);
        } else {
          // Create new chat entry for this itinerary
          const newChats: ItineraryChats = {
            itineraryId,
            sessions: [],
            activeSessionId: null
          };
          setItineraryChats(newChats);
        }
      } else {
        // No stored chats, create new entry
        const newChats: ItineraryChats = {
          itineraryId,
          sessions: [],
          activeSessionId: null
        };
        setItineraryChats(newChats);
      }
    } catch (error) {
      console.error('Error loading chat sessions from sessionStorage:', error);
      // Create new chat entry on error
      const newChats: ItineraryChats = {
        itineraryId,
        sessions: [],
        activeSessionId: null
      };
      setItineraryChats(newChats);
    } finally {
      setIsLoaded(true);
    }
  }, [itineraryId]);

  // Save chat sessions to sessionStorage
  const saveToSessionStorage = (chats: ItineraryChats) => {
    try {
      // Filter out sessions with no exchanges before saving
      const filteredChats: ItineraryChats = {
        ...chats,
        sessions: chats.sessions.filter(session => session.exchanges.length > 0)
      };

      const stored = sessionStorage.getItem(STORAGE_KEY);
      let allChats: ItineraryChats[] = stored ? JSON.parse(stored) : [];
      
      // Update or add the current itinerary's chats
      const existingIndex = allChats.findIndex(chat => chat.itineraryId === filteredChats.itineraryId);
      if (existingIndex >= 0) {
        allChats[existingIndex] = filteredChats;
      } else {
        allChats.push(filteredChats);
      }
      
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(allChats));
    } catch (error) {
      console.error('Error saving chat sessions to sessionStorage:', error);
    }
  };

  // Create a new chat session
  const createNewChat = () => {
    if (!itineraryChats) return;

    // Check if current active session has actual exchanges (user messages + AI responses)
    const currentActiveSession = itineraryChats.sessions.find(
      session => session.id === itineraryChats.activeSessionId
    );

    if (currentActiveSession) {
      // If current session has no exchanges, don't create a new chat
      if (currentActiveSession.exchanges.length === 0) {
        return; // Current session is empty, don't create a new one
      }
    }

    const newSession: ChatSession = {
      id: Date.now().toString(),
      name: `Chat ${itineraryChats.sessions.length + 1}`,
      messages: [
        {
          id: 'ai-greeting',
          content: "Hi! I'm your AI travel assistant. I can help you with questions about your itineraries, suggest modifications, or answer any travel-related questions. What would you like to know?",
          sender: 'ai',
          timestamp: new Date()
        }
      ],
      exchanges: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };

    const updatedChats: ItineraryChats = {
      ...itineraryChats,
      sessions: [newSession, ...itineraryChats.sessions],
      activeSessionId: newSession.id
    };

    setItineraryChats(updatedChats);
    // Save the new session immediately so it's available for interaction
    saveToSessionStorage(updatedChats);
  };

  // Load a specific chat session
  const loadChatSession = (sessionId: string) => {
    if (!itineraryChats) return;

    const updatedChats: ItineraryChats = {
      ...itineraryChats,
      activeSessionId: sessionId
    };

    setItineraryChats(updatedChats);
    saveToSessionStorage(updatedChats);
  };

  // Add an exchange to the active session
  const addExchange = (userMessage: ChatMessage, aiMessage: ChatMessage) => {
    if (!itineraryChats || !itineraryChats.activeSessionId) return;

    const newExchange: ChatExchange = {
      id: Date.now().toString(),
      userMessage,
      aiMessage,
    };

    const updatedSessions = itineraryChats.sessions.map(session => {
      if (session.id === itineraryChats.activeSessionId) {
        // Check if this is the first exchange (session has no exchanges yet)
        const isFirstExchange = session.exchanges.length === 0;
        
        return {
          ...session,
          exchanges: [...(session.exchanges || []), newExchange],
          // Auto-rename session to user's first question if this is the first exchange
          name: isFirstExchange ? truncateText(userMessage.content) : session.name,
          updatedAt: new Date(),
        };
      }
      return session;
    });

    const updatedChats: ItineraryChats = {
      ...itineraryChats,
      sessions: updatedSessions,
    };

    setItineraryChats(updatedChats);
    saveToSessionStorage(updatedChats);
  };

  // Delete a chat session
  const deleteChatSession = (sessionId: string) => {
    if (!itineraryChats) return;

    const updatedSessions = itineraryChats.sessions.filter(session => session.id !== sessionId);
    let newActiveSessionId = itineraryChats.activeSessionId;

    // If we're deleting the active session, switch to the first available session
    if (sessionId === itineraryChats.activeSessionId) {
      newActiveSessionId = updatedSessions.length > 0 ? updatedSessions[0].id : null;
    }

    const updatedChats: ItineraryChats = {
      ...itineraryChats,
      sessions: updatedSessions,
      activeSessionId: newActiveSessionId
    };

    setItineraryChats(updatedChats);
    saveToSessionStorage(updatedChats);
  };

  // Rename a chat session
  const renameChatSession = (sessionId: string, newName: string) => {
    if (!itineraryChats) return;

    const updatedSessions = itineraryChats.sessions.map(session => {
      if (session.id === sessionId) {
        return {
          ...session,
          name: newName
        };
      }
      return session;
    });

    const updatedChats: ItineraryChats = {
      ...itineraryChats,
      sessions: updatedSessions
    };

    setItineraryChats(updatedChats);
    saveToSessionStorage(updatedChats);
  };



  // Get the active session
  const activeSession = itineraryChats?.sessions.find(
    session => session.id === itineraryChats.activeSessionId
  ) || null;

  return {
    itineraryChats,
    activeSession,
    isLoaded,
    createNewChat,
    loadChatSession,
    addExchange,
    deleteChatSession,
    renameChatSession
  };
}; 