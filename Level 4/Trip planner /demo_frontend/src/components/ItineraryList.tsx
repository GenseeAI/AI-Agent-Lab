import { SavedItinerary } from "@/services/itineraryService";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, MapPin, Users, DollarSign, Trash2, X } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface ItineraryListProps {
  itineraries: SavedItinerary[];
  selectedItinerary: SavedItinerary | null;
  onSelectItinerary: (itinerary: SavedItinerary) => void;
  onDeleteItinerary: (id: string) => void;
  onClearAll: () => void;
}

const ItineraryList = ({ 
  itineraries, 
  selectedItinerary, 
  onSelectItinerary, 
  onDeleteItinerary, 
  onClearAll 
}: ItineraryListProps) => {
  if (itineraries.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <MapPin className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold text-muted-foreground mb-2">No Itineraries Yet</h3>
        <p className="text-muted-foreground">
          Start planning your first trip to see your itineraries here!
        </p>
      </div>
    );
  }

  const handleDeleteClick = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    onDeleteItinerary(id);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Your Itineraries ({itineraries.length})</h2>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={onClearAll}
          className="text-destructive hover:text-destructive"
        >
          <X className="h-4 w-4 mr-1" />
          Clear All
        </Button>
      </div>
      
      {itineraries.map((itinerary) => (
        <Card 
          key={itinerary.id}
          className={`cursor-pointer transition-all hover:shadow-md relative group ${
            selectedItinerary?.id === itinerary.id 
              ? 'ring-2 ring-primary bg-primary/5' 
              : 'hover:bg-muted/50'
          }`}
          onClick={() => onSelectItinerary(itinerary)}
        >
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-base font-medium leading-tight mb-2">
                  {itinerary.title}
                </CardTitle>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  <span>{formatDistanceToNow(itinerary.createdAt, { addSuffix: true })}</span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {itinerary.input.method}
                </Badge>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity text-muted-foreground hover:text-destructive"
                  onClick={(e) => handleDeleteClick(e, itinerary.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="pt-0">
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              {itinerary.input.method !== 'natural' && (
                <>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    <span>{(itinerary.input as any).destination}</span>
                  </div>
                  
                  {(itinerary.input as any).duration && (
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      <span>{(itinerary.input as any).duration}</span>
                    </div>
                  )}
                  
                  {(itinerary.input as any).people && (
                    <div className="flex items-center gap-1">
                      <Users className="h-3 w-3" />
                      <span>{(itinerary.input as any).people}</span>
                    </div>
                  )}
                  
                  {(itinerary.input as any).budget && (
                    <div className="flex items-center gap-1">
                      <DollarSign className="h-3 w-3" />
                      <span>${(itinerary.input as any).budget}</span>
                    </div>
                  )}
                </>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

export default ItineraryList; 