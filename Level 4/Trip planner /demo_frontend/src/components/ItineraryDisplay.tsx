import { SavedItinerary, getInputSummary } from "@/services/itineraryService";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Copy, Download, Calendar, MapPin, Users, DollarSign, MessageSquare } from "lucide-react";
import { format } from "date-fns";
import MarkdownIt from "markdown-it";

interface ItineraryDisplayProps {
  itinerary: SavedItinerary | null;
}

const ItineraryDisplay = ({ itinerary }: ItineraryDisplayProps) => {
  if (!itinerary) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold text-muted-foreground mb-2">No Itinerary Selected</h3>
        <p className="text-muted-foreground">
          Select an itinerary from the list to view its details
        </p>
      </div>
    );
  }

  const handleCopyItinerary = () => {
    navigator.clipboard.writeText(itinerary.markdown);
  };

  const handleDownloadItinerary = () => {
    const blob = new Blob([itinerary.markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${itinerary.title.replace(/[^a-zA-Z0-9]/g, '-')}-itinerary.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderMarkdownContext = (markdown: string) => {
    const md = new MarkdownIt();
    return md.render(markdown);
  };
 
  const renderInputDetails = () => {
    const { input } = itinerary;
    
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <Badge variant="secondary">{input.method} input</Badge>
          <span className="text-xs text-muted-foreground">
            {format(itinerary.createdAt, 'PPP p')}
          </span>
        </div>
        
        {input.method === 'natural' ? (
          <div className="space-y-2">
            <h4 className="font-medium text-sm">Original Description:</h4>
            <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
              {input.description}
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Destination:</span>
              <span>{(input as any).destination}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Duration:</span>
              <span>{(input as any).duration}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">People:</span>
              <span>{(input as any).people}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">Budget:</span>
              <span>${(input as any).budget}</span>
            </div>
            
            {(input as any).specialRequests && (
              <div className="col-span-2 space-y-2">
                <h4 className="font-medium text-sm">Special Requests:</h4>
                <p className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
                  {(input as any).specialRequests}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };
  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg">{itinerary.title}</CardTitle>
              <CardDescription>
                Generated {format(itinerary.createdAt, 'PPP')}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleCopyItinerary}
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={handleDownloadItinerary}
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {renderInputDetails()}
        </CardContent>
      </Card>

      {/* Itinerary Content */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Your Travel Itinerary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="bg-muted/30 border rounded-lg p-6 max-h-96 overflow-y-auto">
            <div 
              className="prose prose-lg max-w-none prose-headings:text-foreground prose-p:text-foreground prose-strong:text-foreground prose-ul:text-foreground prose-ol:text-foreground prose-li:text-foreground prose-h1:text-2xl prose-h1:font-bold prose-h1:mb-4 prose-h2:text-xl prose-h2:font-semibold prose-h2:mb-3 prose-h3:text-lg prose-h3:font-medium prose-h3:mb-2 prose-p:mb-3 prose-p:leading-relaxed"
              dangerouslySetInnerHTML={{ __html: renderMarkdownContext(itinerary.markdown) }}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ItineraryDisplay; 