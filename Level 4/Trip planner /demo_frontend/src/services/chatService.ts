import { sendChatMessageToAPI, testChatAPIConnection } from './apiService';
import { SavedItinerary } from './itineraryService';

/**
 * Send a message to the chat API with optional itinerary context
 * @param question - The user's question/message
 * @param itinerary - Optional itinerary context to provide to the AI
 * @returns Promise<string> - The AI's response
 */
export const sendChatMessage = async (question: string, itinerary?: SavedItinerary): Promise<string> => {
  try {
    // Prepare itinerary context if available
    let itineraryContext = '';
    if (itinerary) {
      itineraryContext = `
Itinerary Context:
Title: ${itinerary.title}
Input Method: ${itinerary.input.method}
Created: ${itinerary.createdAt.toLocaleDateString()}

Itinerary Details:
${itinerary.markdown}

Please use this itinerary information to provide relevant and specific answers to the user's questions.
`;
    }

    // Delegate API call to centralized service
    return await sendChatMessageToAPI(question, itineraryContext);
    
  } catch (error) {
    console.error('Error in chat service:', error);
    throw new Error(`Failed to send chat message: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Test the chat API connection
 * @returns Promise<boolean> - True if API is accessible
 */
export { testChatAPIConnection }; 