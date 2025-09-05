import { useState, useEffect } from 'react';
import { SavedItinerary } from '@/services/itineraryService';

const STORAGE_KEY = 'Gensee-Trip-itineraries';

export const useSessionStorage = () => {
  const [savedItineraries, setSavedItineraries] = useState<SavedItinerary[]>([]);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load itineraries from sessionStorage on component mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Convert createdAt strings back to Date objects
        const itineraries = parsed.map((itinerary: any) => ({
          ...itinerary,
          createdAt: new Date(itinerary.createdAt)
        }));
        setSavedItineraries(itineraries);
      }
    } catch (error) {
      console.error('Error loading itineraries from sessionStorage:', error);
    } finally {
      setIsLoaded(true);
    }
  }, []);

  // Save itineraries to sessionStorage whenever they change
  const saveToSessionStorage = (itineraries: SavedItinerary[]) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(itineraries));
    } catch (error) {
      console.error('Error saving itineraries to sessionStorage:', error);
    }
  };

  // Add a new itinerary
  const addItinerary = (itinerary: SavedItinerary) => {
    const updatedItineraries = [itinerary, ...savedItineraries];
    setSavedItineraries(updatedItineraries);
    saveToSessionStorage(updatedItineraries);
  };

  // Remove an itinerary
  const removeItinerary = (id: string) => {
    const updatedItineraries = savedItineraries.filter(it => it.id !== id);
    setSavedItineraries(updatedItineraries);
    saveToSessionStorage(updatedItineraries);
  };

  // Clear all itineraries
  const clearItineraries = () => {
    setSavedItineraries([]);
    sessionStorage.removeItem(STORAGE_KEY);
  };

  return {
    savedItineraries,
    addItinerary,
    removeItinerary,
    clearItineraries,
    isLoaded
  };
}; 