import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { MessageCircle, FileText, Globe, Sparkles, MapPin, Mountain, Building, Binoculars, Utensils } from "lucide-react";
import InteractiveGlobe, { CATEGORIES, Category } from "./InteractiveGlobe";
import { generateItinerary, ItineraryInput } from "@/services/itineraryService";

interface TripPlannerTabsProps {
  onItineraryGenerated: (input: ItineraryInput, markdown: string) => void;
}

const TripPlannerTabs = ({ onItineraryGenerated }: TripPlannerTabsProps) => {
  const [activeTab, setActiveTab] = useState("natural");
  const [randomDestination, setRandomDestination] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<Category>("All");
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDestinationSelected = (destination: string) => {
    setRandomDestination(destination);
  };

  const handleGenerateItinerary = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      let input: ItineraryInput;

      switch (activeTab) {
        case 'natural':
          const naturalInput = (document.getElementById('natural-input') as HTMLTextAreaElement)?.value;
          if (!naturalInput || naturalInput.trim().length < 10) {
            throw new Error('Please provide a detailed description of your dream trip (at least 10 characters)');
          }
          input = {
            method: 'natural' as const,
            description: naturalInput.trim()
          };
          break;

        case 'structured':
          const destination = (document.getElementById('destination') as HTMLInputElement)?.value || '';
          const budget = parseInt((document.getElementById('budget') as HTMLInputElement)?.value || '0');
          const duration = (document.getElementById('duration') as HTMLInputElement)?.value || '';
          const people = parseInt((document.getElementById('people') as HTMLInputElement)?.value || '0');
          
          if (!destination || !budget || !duration || !people) {
            throw new Error('Please fill in all required fields: destination, budget, duration, and number of people');
          }
          if (budget <= 0) {
            throw new Error('Budget must be greater than 0');
          }
          if (people <= 0) {
            throw new Error('Number of people must be greater than 0');
          }
          
          input = {
            method: 'structured' as const,
            destination,
            budget,
            duration,
            people,
            specialRequests: (document.getElementById('requests') as HTMLTextAreaElement)?.value || ''
          };
          break;

        case 'random':
          if (!randomDestination) {
            throw new Error('Please spin the globe to select a destination first');
          }
          const randomBudget = parseInt((document.getElementById('random-budget') as HTMLInputElement)?.value || '0');
          const randomDuration = (document.getElementById('random-duration') as HTMLInputElement)?.value || '';
          const randomPeople = parseInt((document.getElementById('random-people') as HTMLInputElement)?.value || '0');
          
          if (!randomBudget || !randomDuration || !randomPeople) {
            throw new Error('Please fill in budget, duration, and number of people');
          }
          if (randomBudget <= 0) {
            throw new Error('Budget must be greater than 0');
          }
          if (randomPeople <= 0) {
            throw new Error('Number of people must be greater than 0');
          }
          
          input = {
            method: 'random' as const,
            destination: randomDestination,
            budget: randomBudget,
            duration: randomDuration,
            people: randomPeople,
            specialRequests: (document.getElementById('random-requests') as HTMLInputElement)?.value || ''
          };
          break;

        default:
          throw new Error('Invalid tab selected');
      }

      const markdown = await generateItinerary(input);
      onItineraryGenerated(input, markdown);
      
      // Clear form after successful generation
      clearForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred while generating your itinerary');
    } finally {
      setIsGenerating(false);
    }
  };

  const clearForm = () => {
    // Clear all form inputs
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach((input) => {
      if (input instanceof HTMLInputElement || input instanceof HTMLTextAreaElement) {
        input.value = '';
      }
    });
    setRandomDestination('');
    setSelectedCategory('All');
  };

  const getCategoryIcon = (category: Category) => {
    switch (category) {
      case "All": return <Globe className="h-4 w-4" />;
      case "Beachy": return <MapPin className="h-4 w-4" />;
      case "Adventurous": return <Mountain className="h-4 w-4" />;
      case "City Life": return <Building className="h-4 w-4" />;
      case "Wildlife": return <Binoculars className="h-4 w-4" />;
      case "Food": return <Utensils className="h-4 w-4" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">Error: {error}</p>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 mb-8">
          <TabsTrigger value="natural" className="flex items-center space-x-2">
            <MessageCircle className="h-4 w-4" />
            <span>Tell Us Your Dream</span>
          </TabsTrigger>
          <TabsTrigger value="structured" className="flex items-center space-x-2">
            <FileText className="h-4 w-4" />
            <span>Plan Details</span>
          </TabsTrigger>
          <TabsTrigger value="random" className="flex items-center space-x-2">
            <Globe className="h-4 w-4" />
            <span>Surprise Me</span>
          </TabsTrigger>
        </TabsList>

        {/* Natural Language Tab */}
        <TabsContent value="natural">
          <Card className="card-gradient card-shadow">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2 text-2xl">
                <MessageCircle className="h-6 w-6 text-primary" />
                <span>Describe Your Perfect Trip</span>
              </CardTitle>
              <CardDescription className="text-lg">
                Tell us about your dream vacation in your own words
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-3">
                <Label htmlFor="natural-input" className="text-base font-medium">
                  What's your ideal travel experience?
                </Label>
                <Textarea
                  id="natural-input"
                  placeholder="Example: I want a 5-day romantic getaway to Europe under $3000 for 2 people. We love historic sites, cozy cafes, and scenic walks..."
                  className="min-h-[120px] text-base"
                />
              </div>
              
              <div className="bg-secondary/50 p-4 rounded-lg">
                <h4 className="font-medium mb-2 text-primary">💡 Need inspiration? Try these examples:</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• "Adventure trip to Asia for 2 weeks, budget $4000, love hiking and street food"</li>
                  <li>• "Relaxing beach vacation for 7 days, family of 4, under $2500"</li>
                  <li>• "Solo cultural trip to South America, 10 days, budget flexible"</li>
                </ul>
              </div>
              
              <Button 
                size="lg" 
                className="w-full hero-gradient text-white text-lg py-6"
                onClick={handleGenerateItinerary}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Generating Itinerary...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Generate My Travel Itinerary
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Structured Form Tab */}
        <TabsContent value="structured">
          <Card className="card-gradient card-shadow">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2 text-2xl">
                <FileText className="h-6 w-6 text-primary" />
                <span>Trip Details</span>
              </CardTitle>
              <CardDescription className="text-lg">
                Fill in the details for a customized itinerary
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Label htmlFor="destination" className="text-base font-medium">
                    Destination
                  </Label>
                  <Input
                    id="destination"
                    placeholder="e.g., Paris, France"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="budget" className="text-base font-medium">
                    Budget (USD)
                  </Label>
                  <Input
                    id="budget"
                    type="number"
                    placeholder="e.g., 3000"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="duration" className="text-base font-medium">
                    Trip Duration
                  </Label>
                  <Input
                    id="duration"
                    placeholder="e.g., 5 days"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="people" className="text-base font-medium">
                    Number of People
                  </Label>
                  <Input
                    id="people"
                    type="number"
                    placeholder="e.g., 2"
                    className="text-base"
                  />
                </div>
              </div>
              
              <div className="space-y-3">
                <Label htmlFor="requests" className="text-base font-medium">
                  Special Requests or Preferences
                </Label>
                <Textarea
                  id="requests"
                  placeholder="e.g., Vegetarian meals, accessible accommodations, family-friendly activities..."
                  className="min-h-[100px] text-base"
                />
              </div>
              
              <Button 
                size="lg" 
                className="w-full hero-gradient text-white text-lg py-6"
                onClick={handleGenerateItinerary}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Generating Itinerary...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Generate My Travel Itinerary
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Random Destination Tab */}
        <TabsContent value="random">
          <Card className="card-gradient card-shadow">
            <CardHeader className="text-center">
              <CardTitle className="flex items-center justify-center space-x-2 text-2xl">
                <Globe className="h-6 w-6 text-primary" />
                <span>Adventure Awaits</span>
              </CardTitle>
              <CardDescription className="text-lg">
                Let fate decide your next destination
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Category Selection */}
              <div className="space-y-3">
                <Label className="text-base font-medium">
                  Choose Your Adventure Type
                </Label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {CATEGORIES.map((category) => (
                    <Button
                      key={category}
                      variant={selectedCategory === category ? "default" : "outline"}
                      size="sm"
                      onClick={() => setSelectedCategory(category)}
                      className="flex items-center space-x-2 justify-start"
                    >
                      {getCategoryIcon(category)}
                      <span>{category}</span>
                    </Button>
                  ))}
                </div>
                {selectedCategory !== "All" && (
                  <p className="text-sm text-muted-foreground">
                    Selected: <span className="font-medium text-primary">{selectedCategory}</span> destinations only
                  </p>
                )}
              </div>
              
              {/* Interactive Globe */}
              <InteractiveGlobe 
                onDestinationSelected={handleDestinationSelected}
                selectedCategory={selectedCategory}
              />
              
              {/* Form fields (same as structured but destination will be auto-filled) */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3 md:col-span-2">
                  <Label htmlFor="random-destination" className="text-base font-medium">
                    Mystery Destination
                  </Label>
                  <Input
                    id="random-destination"
                    placeholder="Click 'Spin the Globe' to reveal..."
                    value={randomDestination}
                    disabled
                    className="text-base bg-muted"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="random-budget" className="text-base font-medium">
                    Budget (USD)
                  </Label>
                  <Input
                    id="random-budget"
                    type="number"
                    placeholder="e.g., 3000"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="random-duration" className="text-base font-medium">
                    Trip Duration
                  </Label>
                  <Input
                    id="random-duration"
                    placeholder="e.g., 5 days"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="random-people" className="text-base font-medium">
                    Number of People
                  </Label>
                  <Input
                    id="random-people"
                    type="number"
                    placeholder="e.g., 2"
                    className="text-base"
                  />
                </div>
                
                <div className="space-y-3">
                  <Label htmlFor="random-requests" className="text-base font-medium">
                    Special Requests
                  </Label>
                  <Input
                    id="random-requests"
                    placeholder="Any preferences..."
                    className="text-base"
                  />
                </div>
              </div>
              
              <Button 
                size="lg" 
                className="w-full hero-gradient text-white text-lg py-6"
                onClick={handleGenerateItinerary}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Generating Itinerary...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5 mr-2" />
                    Generate My Travel Itinerary
                  </>
                )}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TripPlannerTabs;