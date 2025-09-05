import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Send, Bot, User, Sparkles } from "lucide-react";
import { sendChatMessage } from "@/services/chatService";
import { useChatSessions } from "@/hooks/use-chat-sessions";
import ChatSessionSelector from "./ChatSessionSelector";
import { ChatMessage, ChatExchange } from "@/types/chat";
import { SavedItinerary } from "@/services/itineraryService";

interface AIChatBoxProps {
  selectedItinerary: SavedItinerary | null;
}

const AIChatBox = ({ selectedItinerary }: AIChatBoxProps) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [pendingUserMessage, setPendingUserMessage] = useState<ChatMessage | null>(null);

  const {
    itineraryChats,
    activeSession,
    isLoaded,
    createNewChat,
    loadChatSession,
    addExchange,
    deleteChatSession,
    renameChatSession
  } = useChatSessions(selectedItinerary?.id || null);

  // Auto-create a new chat session if none exists and an itinerary is selected
  useEffect(() => {
    if (isLoaded && selectedItinerary && itineraryChats && itineraryChats.sessions.length === 0) {
      createNewChat();
    }
  }, [isLoaded, selectedItinerary, itineraryChats, createNewChat]);



  const handleSendMessage = async () => {
    if (!inputValue.trim() || !activeSession) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setPendingUserMessage(userMessage);
    const currentInput = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Call the chat API with itinerary context
      const aiResponseText = await sendChatMessage(currentInput, selectedItinerary);
      
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: aiResponseText,
        sender: 'ai',
        timestamp: new Date()
      };
      
      addExchange(userMessage, aiResponse);
    } catch (error) {
      // Handle error by showing an error message
      const aiResponse: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: "I'm sorry, I encountered an error while processing your request. Please try again.",
        sender: 'ai',
        timestamp: new Date()
      };
      
      addExchange(userMessage, aiResponse);
      console.error('Chat API error:', error);
    } finally {
      setPendingUserMessage(null);
      setIsLoading(false);
    }
  };

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (shouldAutoScroll && scrollAreaRef.current) {
      const scrollViewport = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]') as HTMLElement;
      if (scrollViewport) {
        scrollViewport.scrollTop = scrollViewport.scrollHeight;
      }
    }
  }, [activeSession?.messages, activeSession?.exchanges, shouldAutoScroll]);

  // Handle scroll events to determine if we should auto-scroll
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const scrollViewport = e.currentTarget.querySelector('[data-radix-scroll-area-viewport]') as HTMLElement;
    if (scrollViewport) {
      const { scrollTop, scrollHeight, clientHeight } = scrollViewport;
      const isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
      setShouldAutoScroll(isAtBottom);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!selectedItinerary) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-3 flex-shrink-0">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="h-5 w-5 text-primary" />
            AI Travel Assistant
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <div className="text-center text-muted-foreground">
            <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Select an itinerary to start chatting with your AI travel assistant</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!isLoaded) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-3 flex-shrink-0">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Bot className="h-5 w-5 text-primary" />
            AI Travel Assistant
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-3 flex-shrink-0">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Bot className="h-5 w-5 text-primary" />
          AI Travel Assistant
        </CardTitle>
        
        {/* Chat Session Selector */}
        {itineraryChats && (
          <div className="mt-2">
            <ChatSessionSelector
              sessions={itineraryChats.sessions}
              activeSessionId={itineraryChats.activeSessionId}
              onSelectSession={loadChatSession}
              onCreateNewChat={createNewChat}
              onDeleteSession={deleteChatSession}
              onRenameSession={renameChatSession}
            />
          </div>
        )}
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col p-0 min-h-0 overflow-hidden">
        {/* Chat Messages Container */}
        <div className="flex-1 overflow-hidden">
          <ScrollArea 
            className="h-full px-4"
            ref={scrollAreaRef}
            onScroll={handleScroll}
          >
            <div className="space-y-4 py-4">
              {/* Render standalone messages (like initial AI greeting) */}
              {activeSession?.messages?.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-3 ${
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.sender === 'ai' && (
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-[80%] rounded-lg px-3 py-2 ${
                      message.sender === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                    </p>
                  </div>
                  
                  {message.sender === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                </div>
              ))}
              
              {/* Render exchanges (user-AI conversation pairs) */}
              {activeSession?.exchanges?.map((exchange) => (
                <div key={exchange.id}>
                  <div className="flex gap-3 justify-end mb-3">
                    <div className="max-w-[80%] rounded-lg px-3 py-2 bg-primary text-primary-foreground">
                      <p className="text-sm whitespace-pre-wrap">{exchange.userMessage.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {exchange.userMessage.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                      <User className="h-4 w-4 text-primary-foreground" />
                    </div>
                  </div>
                  <div className="flex gap-3 justify-start">
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-4 w-4 text-primary" />
                    </div>
                    <div className="max-w-[80%] rounded-lg px-3 py-2 bg-muted">
                      <p className="text-sm whitespace-pre-wrap">{exchange.aiMessage.content}</p>
                      <p className="text-xs opacity-70 mt-1">
                        {exchange.aiMessage.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
              
              {/* Render pending user message */}
              {pendingUserMessage && (
                <div className="flex gap-3 justify-end">
                  <div className="max-w-[80%] rounded-lg px-3 py-2 bg-primary text-primary-foreground">
                    <p className="text-sm whitespace-pre-wrap">{pendingUserMessage.content}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {pendingUserMessage.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                  <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                    <User className="h-4 w-4 text-primary-foreground" />
                  </div>
                </div>
              )}
              
              {/* Render loading state */}
              {isLoading && (
                <div className="flex gap-3 justify-start">
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Bot className="h-4 w-4 text-primary" />
                  </div>
                  <div className="bg-muted rounded-lg px-3 py-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
        
        {/* Input Container */}
        <div className="border-t p-4 flex-shrink-0 bg-background">
          <div className="flex gap-2">
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your itinerary..."
              className="flex-1"
              disabled={isLoading || !activeSession}
            />
            <Button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading || !activeSession}
              size="sm"
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
          
          {selectedItinerary && (
            <div className="mt-2 text-xs text-muted-foreground">
              💡 You can ask about: modifications, budget, weather, restaurants, activities, transportation
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default AIChatBox; 