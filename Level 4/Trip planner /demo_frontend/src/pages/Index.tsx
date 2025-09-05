import { useState } from "react";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import TripPlannerTabs from "@/components/TripPlannerTabs";
import ItineraryList from "@/components/ItineraryList";
import ItineraryDisplay from "@/components/ItineraryDisplay";
import AIChatBox from "@/components/AIChatBox";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { SavedItinerary, ItineraryInput, generateItineraryTitle } from "@/services/itineraryService";
import { useSessionStorage } from "@/hooks/use-session-storage";

const Index = () => {
  const [activeView, setActiveView] = useState<'plan' | 'itineraries'>('plan');
  const [selectedItinerary, setSelectedItinerary] = useState<SavedItinerary | null>(null);
  const { savedItineraries, addItinerary, removeItinerary, clearItineraries, isLoaded } = useSessionStorage();

  const handleItineraryGenerated = (input: ItineraryInput, markdown: string) => {
    const newItinerary: SavedItinerary = {
      id: Date.now().toString(), // In a real app, use a proper UUID
      title: generateItineraryTitle(input),
      input,
      markdown,
      createdAt: new Date(),
    };

    addItinerary(newItinerary);
    setSelectedItinerary(newItinerary);
    setActiveView('itineraries');
  };

  const handleSelectItinerary = (itinerary: SavedItinerary) => {
    setSelectedItinerary(itinerary);
  };

  const handleDeleteItinerary = (id: string) => {
    removeItinerary(id);
    if (selectedItinerary?.id === id) {
      setSelectedItinerary(null);
    }
  };

  const handleClearAllItineraries = () => {
    clearItineraries();
    setSelectedItinerary(null);
  };

  const renderPlanView = () => (
    <>
      <Hero />
      <div className="container mx-auto px-4 py-8">
        <Card className="card-gradient card-shadow">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl md:text-4xl font-bold mb-4">
              Plan Your Perfect Trip
            </CardTitle>
            <CardDescription className="text-lg max-w-2xl mx-auto">
              Choose your preferred planning method and let our AI create the perfect itinerary for your next adventure.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <TripPlannerTabs onItineraryGenerated={handleItineraryGenerated} />
          </CardContent>
        </Card>
      </div>
    </>
  );

  const renderItinerariesView = () => (
    <div className="container mx-auto px-4 pt-8 pb-4">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-180px)]">
        {/* Left Column - Itinerary List */}
        <div className="lg:col-span-1 overflow-hidden">
          <Card className="h-full">
            <CardContent className="p-6 h-full overflow-y-auto">
              {!isLoaded ? (
                <div className="flex items-center justify-center h-32">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                </div>
              ) : (
                <ItineraryList
                  itineraries={savedItineraries}
                  selectedItinerary={selectedItinerary}
                  onSelectItinerary={handleSelectItinerary}
                  onDeleteItinerary={handleDeleteItinerary}
                  onClearAll={handleClearAllItineraries}
                />
              )}
            </CardContent>
          </Card>
        </div>

        {/* Middle Column - Itinerary Display */}
        <div className="lg:col-span-2 overflow-hidden">
          <Card className="h-full">
            <CardContent className="p-6 h-full overflow-y-auto">
              <ItineraryDisplay itinerary={selectedItinerary} />
            </CardContent>
          </Card>
        </div>

        {/* Right Column - AI Chat Box */}
        <div className="lg:col-span-1 overflow-hidden">
          <AIChatBox selectedItinerary={selectedItinerary} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-background">
      <Header activeView={activeView} onViewChange={setActiveView} />
      
      <main>
        {activeView === 'plan' ? renderPlanView() : renderItinerariesView()}
      </main>
    </div>
  );
};

export default Index;
