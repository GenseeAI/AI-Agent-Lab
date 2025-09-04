import { Plane } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HeaderProps {
  activeView: 'plan' | 'itineraries';
  onViewChange: (view: 'plan' | 'itineraries') => void;
}

const Header = ({ activeView, onViewChange }: HeaderProps) => {
  return (
    <header className="w-full bg-card/80 backdrop-blur-sm border-b border-border/50 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="relative">
              <img 
                src="/src/assets/eye-only.png" 
                alt="GenseeTrip Logo" 
                className="h-8 w-8" 
              />
              <Plane className="h-4 w-4 text-accent absolute -top-1 -right-1" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">GenseeTrip</h1>
              <p className="text-xs text-muted-foreground">Your AI Travel Companion</p>
            </div>
          </div>
          
          {/* Centered Navigation Tabs */}
          <div className="flex-1 flex justify-center">
            <nav className="flex items-center bg-muted/50 rounded-lg p-1 border border-border/50">
              <Button 
                variant="ghost"
                className={`rounded-md px-6 py-2 transition-all duration-200 ${
                  activeView === 'plan' 
                    ? 'bg-background text-primary shadow-sm border border-border' 
                    : 'text-muted-foreground hover:text-primary hover:bg-muted'
                }`}
                onClick={() => onViewChange('plan')}
              >
                Plan Trip
              </Button>
              <Button 
                variant="ghost"
                className={`rounded-md px-6 py-2 transition-all duration-200 ${
                  activeView === 'itineraries' 
                    ? 'bg-background text-primary shadow-sm border border-border' 
                    : 'text-muted-foreground hover:text-primary hover:bg-muted'
                }`}
                onClick={() => onViewChange('itineraries')}
              >
                My Itineraries
              </Button>
            </nav>
          </div>

          {/* Spacer to balance the layout */}
          <div className="w-[200px]"></div>
        </div>
      </div>
    </header>
  );
};

export default Header;