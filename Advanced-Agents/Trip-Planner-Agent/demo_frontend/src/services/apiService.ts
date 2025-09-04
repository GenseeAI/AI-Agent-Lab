// Backend API Service
// Makes requests to backend endpoints which handle external API configuration

// Common API response structure 
interface BaseAPIResponse {
  status: string;
  response: string;
  stdout: string;
  stderr: string;
  error_code: number;
}

interface ItineraryRequest {
  travel_request: string;
}

export interface ItineraryAPIResponse extends BaseAPIResponse {}

interface ChatRequest {
  question: string;
  itinerary_context?: string;
}

export interface ChatAPIResponse extends BaseAPIResponse {}

// Backend configuration 
const BACKEND_CONFIG = {
  BASE_URL: import.meta.env.VITE_BACKEND_URL,
  ENDPOINTS: {
    ITINERARY: '/api/itinerary',
    CHAT: '/api/chat'
  }
};

const callBackendAPI = async <TRequest, TResponse extends BaseAPIResponse>(
  endpoint: string,
  requestData: TRequest
): Promise<TResponse> => {
  try {
    const response = await fetch(`${BACKEND_CONFIG.BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestData)
    });

    if (!response.ok) {
      throw new Error(`Backend request failed with status: ${response.status}`);
    }

    const data: TResponse = await response.json();
    
    // Handle API response - check for errors first
    if (data.error_code !== 0) {
      throw new Error(`Backend Error (code ${data.error_code}): ${data.stderr || 'Unknown error'}`);
    }
    
    return data;
    
  } catch (error) {
    console.error('Error calling backend API:', error);
    throw new Error(`Failed to call backend API: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Generate itinerary using the backend API
 * @param travelRequest - The travel request string
 * @returns Promise<string> - The generated itinerary in markdown format
 */
export const generateItineraryFromAPI = async (travelRequest: string): Promise<string> => {
  try {
    const requestData: ItineraryRequest = {
      travel_request: travelRequest,
    };

    const data = await callBackendAPI<ItineraryRequest, ItineraryAPIResponse>(
      BACKEND_CONFIG.ENDPOINTS.ITINERARY,
      requestData
    );
    
    // Return the response field which contains the itinerary
    if (data.response) {
      return data.response;
    }
    
    // Fallback if response is empty
    return `# No Itinerary Generated

The backend call was successful but no itinerary was returned.

**Travel Request:** ${travelRequest}

**Status:** ${data.status}`;
    
  } catch (error) {
    console.error('Error calling itinerary backend API:', error);
    throw new Error(`Failed to generate itinerary via backend: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Send a chat message to the backend API
 * @param question - The user's question/message
 * @param itineraryContext - Optional itinerary context to provide to the AI
 * @returns Promise<string> - The AI's response
 */
export const sendChatMessageToAPI = async (question: string, itineraryContext?: string): Promise<string> => {
  try {
    const requestData: ChatRequest = {
      question: question,
      ...(itineraryContext && { itinerary_context: itineraryContext })
    };

    const data = await callBackendAPI<ChatRequest, ChatAPIResponse>(
      BACKEND_CONFIG.ENDPOINTS.CHAT,
      requestData
    );
    
    // Return the response field which contains the AI's reply
    if (data.response) {
      return data.response;
    }
    
    // Fallback if response is empty
    return "I'm sorry, I couldn't generate a response at the moment. Please try again.";
    
  } catch (error) {
    console.error('Error calling chat backend API:', error);
    throw new Error(`Failed to send chat message: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Test the backend connection for itinerary generation
 * @returns Promise<boolean> - True if backend is accessible
 */
export const testAPIConnection = async (): Promise<boolean> => {
  try {
    const testRequest = "Test connection - 2 day trip to Paris for 2 people with $1000 budget";
    await generateItineraryFromAPI(testRequest);
    return true;
  } catch (error) {
    console.error('Backend connection test failed:', error);
    return false;
  }
};

/**
 * Test the chat backend connection
 * @returns Promise<boolean> - True if backend is accessible
 */
export const testChatAPIConnection = async (): Promise<boolean> => {
  try {
    const testQuestion = "Hello, can you help me with travel planning?";
    await sendChatMessageToAPI(testQuestion);
    return true;
  } catch (error) {
    console.error('Chat backend connection test failed:', error);
    return false;
  }
}; 