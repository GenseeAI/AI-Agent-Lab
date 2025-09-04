import { MapPin, Users, Calendar, DollarSign } from "lucide-react";

const Hero = () => {
  return (
    <section className="relative py-20 px-4 overflow-hidden">
      {/* Background with gradient and overlay */}
      <div className="absolute inset-0 hero-gradient opacity-10"></div>
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-background/50 to-background"></div>
      
      {/* Floating elements */}
      <div className="absolute top-20 left-10 w-4 h-4 bg-accent rounded-full animate-float opacity-60"></div>
      <div className="absolute top-40 right-20 w-6 h-6 bg-primary rounded-full animate-float opacity-40" style={{animationDelay: '1s'}}></div>
      <div className="absolute bottom-40 left-20 w-3 h-3 bg-secondary rounded-full animate-float opacity-50" style={{animationDelay: '2s'}}></div>
      
      <div className="container mx-auto text-center relative z-10">
        <div className="max-w-4xl mx-auto">
          {/* Main heading */}
          <h1 className="text-5xl md:text-7xl font-bold mb-6 animate-fade-in-up">
            Plan Your Perfect
            <span className="block text-gradient">Adventure</span>
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-muted-foreground mb-12 animate-fade-in-up max-w-3xl mx-auto" style={{animationDelay: '0.2s'}}>
            From spontaneous getaways to detailed itineraries, let AI craft your ideal travel experience with personalized recommendations and smart planning.
          </p>
          
          {/* Feature highlights */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16 animate-fade-in-up" style={{animationDelay: '0.4s'}}>
            <div className="flex flex-col items-center space-y-3 p-4 rounded-lg bg-card/50 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <MapPin className="h-6 w-6 text-primary" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold mb-1">Any Destination</h3>
                <p className="text-sm text-muted-foreground">Global coverage</p>
              </div>
            </div>
            
            <div className="flex flex-col items-center space-y-3 p-4 rounded-lg bg-card/50 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
                <DollarSign className="h-6 w-6 text-accent" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold mb-1">Smart Budgeting</h3>
                <p className="text-sm text-muted-foreground">Cost optimization</p>
              </div>
            </div>
            
            <div className="flex flex-col items-center space-y-3 p-4 rounded-lg bg-card/50 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Calendar className="h-6 w-6 text-primary" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold mb-1">Flexible Dates</h3>
                <p className="text-sm text-muted-foreground">Any duration</p>
              </div>
            </div>
            
            <div className="flex flex-col items-center space-y-3 p-4 rounded-lg bg-card/50 backdrop-blur-sm">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
                <Users className="h-6 w-6 text-accent" />
              </div>
              <div className="text-center">
                <h3 className="font-semibold mb-1">Group Friendly</h3>
                <p className="text-sm text-muted-foreground">Any group size</p>
              </div>
            </div>
          </div>
          
          {/* Trust indicators */}
          <div className="flex flex-wrap justify-center items-center space-x-8 text-muted-foreground text-sm animate-fade-in-up" style={{animationDelay: '0.6s'}}>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>AI-Powered Planning</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Real-time Updates</span>
            </div>
            
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;