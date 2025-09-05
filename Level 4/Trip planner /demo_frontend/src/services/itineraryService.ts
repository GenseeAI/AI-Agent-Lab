import { generateItineraryFromAPI } from './apiService';

// Types for different input methods
export type InputMethod = 'natural' | 'structured' | 'random';

// Base interface for all input types
interface BaseItineraryInput {
  method: InputMethod;
  budget?: number;
  duration?: string;
  people?: number;
  specialRequests?: string;
}

// Natural language input
interface NaturalItineraryInput extends BaseItineraryInput {
  method: 'natural';
  description: string;
}

// Structured form input
interface StructuredItineraryInput extends BaseItineraryInput {
  method: 'structured';
  destination: string;
  budget: number;
  duration: string;
  people: number;
  specialRequests: string;
}

// Random destination input
interface RandomItineraryInput extends BaseItineraryInput {
  method: 'random';
  destination: string; // Auto-filled from globe
  budget: number;
  duration: string;
  people: number;
  specialRequests: string;
}

// Union type for all input types
export type ItineraryInput = NaturalItineraryInput | StructuredItineraryInput | RandomItineraryInput;

// Interface for saved itinerary with metadata
export interface SavedItinerary {
  id: string;
  title: string;
  input: ItineraryInput;
  markdown: string;
  createdAt: Date;
}

/**
 * Main function to generate travel itineraries based on different input methods
 * @param input - The input data with method identifier
 * @returns Promise<string> - The generated itinerary in markdown format
 */
export const generateItinerary = async (input: ItineraryInput): Promise<string> => {
  try {
    // Validate input based on method
    validateInput(input);
    
    // Process input based on method
    const processedData = processInputByMethod(input);
    
    // Generate itinerary using processed data (API call would go here)
    const itinerary = await createItinerary(processedData);
    
    return itinerary;
  } catch (error) {
    console.error('Error generating itinerary:', error);
    throw new Error(`Failed to generate itinerary: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
};

/**
 * Generate a title from the input data
 */
export const generateItineraryTitle = (input: ItineraryInput): string => {
  switch (input.method) {
    case 'natural':
      // Extract destination or create a generic title from description
      const words = input.description.split(' ').slice(0, 6);
      return words.join(' ') + (words.length < input.description.split(' ').length ? '...' : '');
    case 'structured':
    case 'random':
      return `${input.destination} - ${input.duration} - ${input.people} people`;
    default:
      return 'Travel Itinerary';
  }
};

/**
 * Get formatted input summary for display
 */
export const getInputSummary = (input: ItineraryInput): string => {
  switch (input.method) {
    case 'natural':
      return input.description;
    case 'structured':
    case 'random':
      return processInputByMethod(input);
    default:
      return 'No details available';
  }
};

/**
 * Validates input data based on the method type
 */
const validateInput = (input: ItineraryInput): void => {
  switch (input.method) {
    case 'natural':
      if (!input.description || input.description.trim().length < 10) {
        throw new Error('Please provide a detailed description of your dream trip (at least 10 characters)');
      }
      break;
      
    case 'structured':
      if (!input.destination || !input.budget || !input.duration || !input.people) {
        throw new Error('Please fill in all required fields: destination, budget, duration, and number of people');
      }
      if (input.budget <= 0) {
        throw new Error('Budget must be greater than 0');
      }
      if (input.people <= 0) {
        throw new Error('Number of people must be greater than 0');
      }
      break;
      
    case 'random':
      if (!input.destination) {
        throw new Error('Please spin the globe to select a destination first');
      }
      if (!input.budget || !input.duration || !input.people) {
        throw new Error('Please fill in budget, duration, and number of people');
      }
      if (input.budget <= 0) {
        throw new Error('Budget must be greater than 0');
      }
      if (input.people <= 0) {
        throw new Error('Number of people must be greater than 0');
      }
      break;
  }
};

/**
 * Processes input data based on the method type
 */
const processInputByMethod = (input: ItineraryInput): string => {
  switch (input.method) {
    case 'natural':
      return input.description;
    case 'structured':
      return processStructuredInput(input as StructuredItineraryInput);
    case 'random':
      return processRandomInput(input as RandomItineraryInput);
    default:
      throw new Error(`Unknown input method: ${(input as any).method}`);
  }
};

/**
 * Processes structured form input
 */
const processStructuredInput = (input: StructuredItineraryInput): string => {
  if (input.specialRequests) {
    return `I want to plan a trip to ${input.destination} for ${input.duration} days. I am traveling with ${input.people} people with a budget of $${input.budget}. Attach importance to ${input.specialRequests}`;
  } else {
    return `I want to plan a trip to ${input.destination} for ${input.duration} days. I am traveling with ${input.people} people with a budget of $${input.budget}`;
  }
};

/**
 * Processes random destination input
 */
const processRandomInput = (input: RandomItineraryInput): string => {
  if (input.specialRequests) {
    return `I want to plan a trip to ${input.destination} for ${input.duration} days. I am traveling with ${input.people} people with a budget of $${input.budget}. Attach importance to ${input.specialRequests}`;
  } else {
    return `I want to plan a trip to ${input.destination} for ${input.duration} days. I am traveling with ${input.people} people with a budget of $${input.budget}`;
  }
};

/**
 * Creates the actual itinerary using the processed data
 * This integrates with the external API service
 */
const createItinerary = async (data: string): Promise<string> => {
  try {
    // Call the external API to generate the itinerary
    const itinerary = await generateItineraryFromAPI(data);
    return itinerary;
  } catch (error) {
    console.error('Error generating itinerary via API:', error);
    
    // Fallback to a basic itinerary if API fails
    return `# Travel Itinerary

## Trip Overview
**Request:** ${data}

## ⚠️ API Connection Issue
We encountered an issue connecting to our itinerary generation service. Please try again later or contact support if the problem persists.

**Error Details:** ${error instanceof Error ? error.message : 'Unknown error'}

## What to do next:
1. Check your internet connection
2. Try generating the itinerary again
3. If the problem persists, please contact our support team

---

*We apologize for the inconvenience. Our team is working to resolve this issue.*`;
  }
}; 