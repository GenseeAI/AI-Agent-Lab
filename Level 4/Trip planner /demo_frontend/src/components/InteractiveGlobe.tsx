import { useEffect, useRef, useState } from "react";
import Globe from "globe.gl";
import * as THREE from "three";
import { Button } from "@/components/ui/button";
import { Sparkles } from "lucide-react";

// Available categories
export const CATEGORIES = ["All", "Beachy", "Adventurous", "City Life", "Wildlife", "Food"] as const;

export type Category = typeof CATEGORIES[number];

// Curated destinations with their coordinates
const DESTINATIONS = [
  // Beachy
  { name: "Bali, Indonesia", category: "Beachy" as const, lat: -8.3405, lng: 115.0920 },
  { name: "Santorini, Greece", category: "Beachy" as const, lat: 36.3932, lng: 25.4615 },
  { name: "Maldives", category: "Beachy" as const, lat: 3.2028, lng: 73.2207 },
  { name: "Cancun, Mexico", category: "Beachy" as const, lat: 21.1619, lng: -86.8515 },
  { name: "Gold Coast, Australia", category: "Beachy" as const, lat: -28.0167, lng: 153.4000 },
  
  // Adventurous
  { name: "Queenstown, New Zealand", category: "Adventurous" as const, lat: -45.0312, lng: 168.6626 },
  { name: "Interlaken, Switzerland", category: "Adventurous" as const, lat: 46.6863, lng: 7.8632 },
  { name: "Torres del Paine, Chile", category: "Adventurous" as const, lat: -50.9423, lng: -73.4068 },
  { name: "Chamonix, France", category: "Adventurous" as const, lat: 45.9237, lng: 6.8694 },
  { name: "Banff, Canada", category: "Adventurous" as const, lat: 51.4968, lng: -115.9281 },
  
  // City Life
  { name: "Tokyo, Japan", category: "City Life" as const, lat: 35.6762, lng: 139.6503 },
  { name: "New York City, USA", category: "City Life" as const, lat: 40.7128, lng: -74.0060 },
  { name: "London, England", category: "City Life" as const, lat: 51.5074, lng: -0.1278 },
  { name: "Dubai, UAE", category: "City Life" as const, lat: 25.2048, lng: 55.2708 },
  { name: "Singapore", category: "City Life" as const, lat: 1.3521, lng: 103.8198 },
  
  // Wildlife
  { name: "Serengeti, Tanzania", category: "Wildlife" as const, lat: -2.3333, lng: 34.8333 },
  { name: "Kruger National Park, South Africa", category: "Wildlife" as const, lat: -24.0000, lng: 31.5000 },
  { name: "Galápagos Islands, Ecuador", category: "Wildlife" as const, lat: -0.9538, lng: -91.0232 },
  { name: "Costa Rica", category: "Wildlife" as const, lat: 9.7489, lng: -83.7534 },
  { name: "Borneo, Malaysia", category: "Wildlife" as const, lat: 0.9619, lng: 114.5548 },
  
  // Food
  { name: "Bangkok, Thailand", category: "Food" as const, lat: 13.7563, lng: 100.5018 },
  { name: "Istanbul, Turkey", category: "Food" as const, lat: 41.0082, lng: 28.9784 },
  { name: "Lima, Peru", category: "Food" as const, lat: -12.0464, lng: -77.0428 },
  { name: "Barcelona, Spain", category: "Food" as const, lat: 41.3851, lng: 2.1734 },
  { name: "Mumbai, India", category: "Food" as const, lat: 19.0760, lng: 72.8777 }
];

interface InteractiveGlobeProps {
  onDestinationSelected: (destination: string) => void;
  selectedCategory?: Category;
}

const InteractiveGlobe = ({ onDestinationSelected, selectedCategory = "All" }: InteractiveGlobeProps) => {
  const globeRef = useRef<HTMLDivElement>(null);
  const globeInstance = useRef<any>(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState<string>("");
  const [isZoomedIn, setIsZoomedIn] = useState(false);

  // Initialize globe only once on mount
  useEffect(() => {
    if (!globeRef.current) return;

    // Get container dimensions
    const containerRect = globeRef.current.getBoundingClientRect();
    const width = containerRect.width;
    const height = containerRect.height;

    // Initialize Globe
    const globe = new Globe(globeRef.current)
      .globeImageUrl('//unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
      .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
      .backgroundColor('rgba(0,0,0,0)')
      .showAtmosphere(true)
      .atmosphereColor('#3b82f6')
      .atmosphereAltitude(0.1)
      .enablePointerInteraction(false)
      .width(width)
      .height(height);

    // Add country boundaries
    fetch('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson')
      .then(res => res.json())
      .then(countries => {
        globe
          .polygonsData(countries.features)
          .polygonCapColor(() => 'rgba(0, 0, 0, 0)')
          .polygonSideColor(() => 'rgba(255, 255, 255, 0.4)')
          .polygonStrokeColor(() => 'rgba(255, 255, 255, 0.6)')
          .polygonAltitude(0.001);
      });

    globeInstance.current = globe;

    // Set initial view
    globe.pointOfView({ altitude: 2.5 });

    // Handle resize
    const handleResize = () => {
      if (globeRef.current && globeInstance.current) {
        const rect = globeRef.current.getBoundingClientRect();
        globeInstance.current.width(rect.width).height(rect.height);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (globeInstance.current) {
        globeInstance.current._destructor?.();
      }
    };
  }, []);

  // Handle auto-rotation separately
  useEffect(() => {
    if (!globeInstance.current) return;

    let rotateInterval: NodeJS.Timeout | null = null;
    
    const autoRotate = () => {
      if (!isSpinning && !isZoomedIn && globeInstance.current) {
        const { lat, lng } = globeInstance.current.pointOfView();
        globeInstance.current.pointOfView({ lat, lng: lng - 0.3 }, 50);
      }
    };

    // Only start auto-rotate if not zoomed in and not spinning
    if (!isZoomedIn && !isSpinning) {
      rotateInterval = setInterval(autoRotate, 50);
    }

    return () => {
      if (rotateInterval) {
        clearInterval(rotateInterval);
      }
    };
  }, [isSpinning, isZoomedIn]);

  // Get filtered destinations based on selected category
  const getFilteredDestinations = () => {
    if (selectedCategory === "All") {
      return DESTINATIONS;
    }
    return DESTINATIONS.filter(dest => dest.category === selectedCategory);
  };

  const spinAndSelectDestination = async () => {
    if (!globeInstance.current || isSpinning) return;
    
    setIsSpinning(true);
    
    // If already zoomed in, zoom out first
    if (isZoomedIn) {
      globeInstance.current.pointOfView({ altitude: 2.5 }, 1000);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsZoomedIn(false);
      setSelectedDestination("");
      // Clear previous pin and labels
      globeInstance.current.labelsData([]);
      // Remove any existing pin meshes
      const existingPins = globeInstance.current.scene().children.filter((child: any) => 
        child.type === 'Group' && child.children.length === 2 && 
        child.children.some((grandchild: any) => grandchild.geometry && grandchild.geometry.type === 'ConeGeometry')
      );
      existingPins.forEach((pin: any) => globeInstance.current.scene().remove(pin));
    }
    
    // Get filtered destinations and select random destination
    const filteredDestinations = getFilteredDestinations();
    if (filteredDestinations.length === 0) {
      setIsSpinning(false);
      return;
    }
    
    const randomDestination = filteredDestinations[Math.floor(Math.random() * filteredDestinations.length)];
    
    // Calculate the path to destination
    const currentView = globeInstance.current.pointOfView();
    let targetLng = randomDestination.lng;
    
    // Calculate shortest path (considering globe wrap-around)
    const currentLng = currentView.lng;
    const diff = targetLng - currentLng;
    if (diff > 180) targetLng -= 360;
    if (diff < -180) targetLng += 360;
    
    // Spinning animation that slows down and stops at destination
    const totalSpins = 2; // Number of full rotations before slowing down
    const totalDuration = 3000;
    const steps = 120;
    const stepDuration = totalDuration / steps;
    
    for (let i = 0; i < steps; i++) {
      await new Promise(resolve => setTimeout(resolve, stepDuration));
      
      // Calculate easing (fast at start, slow at end)
      const progress = i / steps;
      const easing = 1 - Math.pow(1 - progress, 3); // Cubic easing out
      
      // Calculate position
      const spinAmount = totalSpins * 360 * (1 - Math.pow(1 - progress, 2));
      const finalLng = currentLng + (targetLng - currentLng) * easing + spinAmount;
      const finalLat = currentView.lat + (randomDestination.lat - currentView.lat) * easing * 0.3;
      
      globeInstance.current.pointOfView({ 
        lat: finalLat, 
        lng: finalLng 
      }, 0);
    }
    
    // Create the pin as a custom object
    const createPinMesh = (altitude, scale = 1) => {
      // Create a more realistic pin geometry (cone + sphere for the head)
      const pinGroup = new THREE.Group();
      
      // Pin tip (cone) - larger base size for better visibility
      const tipGeometry = new THREE.ConeGeometry(1.5 * scale, 6 * scale, 8);
      tipGeometry.rotateX(Math.PI); // Point tip down
      tipGeometry.translate(0, 3 * scale, 0); // Move up so tip touches surface
      const tipMaterial = new THREE.MeshPhongMaterial({ 
        color: '#c0c0c0', // Light grey/silver color
        shininess: 100
      });
      const tipMesh = new THREE.Mesh(tipGeometry, tipMaterial);
      
      // Pin head (sphere)
      const headGeometry = new THREE.SphereGeometry(2 * scale, 12, 8);
      headGeometry.translate(0, 8 * scale, 0);
      const headMaterial = new THREE.MeshPhongMaterial({ 
        color: '#dc2626', // Red color
        shininess: 50,
        emissive: '#dc2626',
        emissiveIntensity: 0.05
      });
      const headMesh = new THREE.Mesh(headGeometry, headMaterial);
      
      pinGroup.add(tipMesh);
      pinGroup.add(headMesh);
      
      // Get the globe's coordinate conversion
      const globeRadius = globeInstance.current.getGlobeRadius();
      const coords = globeInstance.current.getCoords(randomDestination.lat, randomDestination.lng, altitude * globeRadius);
      
      // Ensure coords is a proper Vector3
      const position = new THREE.Vector3(coords.x, coords.y, coords.z);
      
      // Set the pin's position
      pinGroup.position.copy(position);
      
      // Calculate the proper orientation for the pin to stand perpendicular to the globe surface
      // The position vector from globe center to surface point IS the normal direction
      const normal = position.clone().normalize();
      
      // Align the pin's up direction (Y-axis) with the normal vector
      const up = new THREE.Vector3(0, 1, 0);
      const quaternion = new THREE.Quaternion();
      quaternion.setFromUnitVectors(up, normal);
      pinGroup.applyQuaternion(quaternion);
      
      // Add a consistent "up right" tilt (about 25 degrees)
      // Calculate east direction (tangent to globe surface pointing east)
      const eastDirection = new THREE.Vector3(-Math.sin(randomDestination.lng * Math.PI / 180), 0, Math.cos(randomDestination.lng * Math.PI / 180));
      
      // Calculate north direction (tangent to globe surface pointing north)
      const northDirection = new THREE.Vector3().crossVectors(eastDirection, normal).normalize();
      
      // Create "down left" direction (southwest on the globe surface)
      const downLeftDirection = new THREE.Vector3()
        .addScaledVector(eastDirection, -0.707)   // 45 degrees towards west
        .addScaledVector(northDirection, -0.707); // 45 degrees towards south
      downLeftDirection.normalize();
      
      // Calculate the tilt axis (perpendicular to both normal and downLeft direction)
      const tiltAxis = new THREE.Vector3().crossVectors(normal, downLeftDirection).normalize();
      
      // Tilt the pin around the tilt axis to make the head point up-right
      const tiltQuaternion = new THREE.Quaternion();
      tiltQuaternion.setFromAxisAngle(tiltAxis, 0.436); // ~25 degrees
      pinGroup.applyQuaternion(tiltQuaternion);
      
      return pinGroup;
    };

    // Add the pin to the globe scene with larger initial scale
    let pinMesh = createPinMesh(0.5, 1.0);
    globeInstance.current.scene().add(pinMesh);
    
    // Animate pin dropping to the surface
    const dropDuration = 1000;
    const dropSteps = 20;
    const dropStepDuration = dropDuration / dropSteps;
    
    for (let i = 0; i <= dropSteps; i++) {
      await new Promise(resolve => setTimeout(resolve, dropStepDuration));
      
      const progress = i / dropSteps;
      // Add a bounce effect at the end
      const bounce = progress >= 0.8 ? Math.sin((progress - 0.8) * 10) * 0.1 * (1 - progress) : 0;
      const altitude = 0.5 * (1 - progress) + bounce;
      
      // Update pin position with larger scale during drop
      globeInstance.current.scene().remove(pinMesh);
      pinMesh = createPinMesh(altitude, 1.0);
      globeInstance.current.scene().add(pinMesh);
    }
    
    // Start zoom animation and pin scaling simultaneously (no pause)
    globeInstance.current.pointOfView({
      lat: randomDestination.lat,
      lng: randomDestination.lng,
      altitude: 0.3
    }, 2000);
    
    // Animate pin scaling down during zoom (truly parallel)
    const zoomDuration = 2000;
    const zoomSteps = 40; // More steps for smoother animation
    const zoomStepDuration = zoomDuration / zoomSteps;
    let currentStep = 0;
    
    const scaleInterval = setInterval(() => {
      currentStep++;
      const progress = currentStep / zoomSteps;
      // Scale from 1.0 down to 0.25 during zoom with easing (smaller final size)
      const easeProgress = 1 - Math.pow(1 - progress, 2); // Ease out
      const scale = 1.0 - (easeProgress * 0.75);
      
      // Update pin with new scale
      globeInstance.current.scene().remove(pinMesh);
      pinMesh = createPinMesh(0, scale); // Pin is now on surface
      globeInstance.current.scene().add(pinMesh);
      
      // Stop when animation is complete
      if (currentStep >= zoomSteps) {
        clearInterval(scaleInterval);
      }
    }, zoomStepDuration);
    
    // Wait for zoom to complete
    await new Promise(resolve => setTimeout(resolve, zoomDuration));
    
    // Reveal destination immediately after zoom completes
    setSelectedDestination(randomDestination.name);
    onDestinationSelected(randomDestination.name);
    setIsZoomedIn(true);
    setIsSpinning(false);
    
    // Add text label directly on the globe
    const labelData = [{
      lat: randomDestination.lat,
      lng: randomDestination.lng,
      text: `${randomDestination.name}`,
      color: 'white',
      size: 1
    }];
    
    globeInstance.current
      .labelsData(labelData)
      .labelText('text')
      .labelColor('color')
      .labelSize('size')
      .labelResolution(2);
  };

  return (
    <div className="bg-gradient-to-b from-slate-900 to-slate-950 rounded-lg p-4 text-center min-h-[400px] flex flex-col">
      <div className="relative flex-1 mx-auto mb-4 w-full">
        <div ref={globeRef} className="w-full h-full min-h-[400px] flex items-center justify-center" />
      </div>
      
      <Button 
        onClick={spinAndSelectDestination}
        disabled={isSpinning}
        className="sunset-gradient text-white mb-4 text-lg px-8 py-3 disabled:opacity-50"
      >
        {isSpinning ? (
          <>
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Spinning Globe...
          </>
        ) : (
          <>
            <Sparkles className="h-5 w-5 mr-2" />
            Spin the Globe
          </>
        )}
      </Button>
      
      <p className="text-muted-foreground">
        {isSpinning 
          ? "Discovering your mystery destination..." 
          : selectedDestination
            ? "Ready to plan your adventure!"
            : "Click to discover your mystery destination!"
        }
      </p>
    </div>
  );
};

export default InteractiveGlobe;