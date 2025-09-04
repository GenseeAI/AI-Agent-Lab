# Trip Planner Agent

A sophisticated multi-agent travel planning system that simulates a collaborative planning session between a travel guide, traveler, and critic to create comprehensive travel itineraries. The agent uses CamelAI's multi-agent framework to generate detailed, personalized travel plans through an interactive planning process.

## Features

- **Multi-Agent Collaboration**: Travel Guide, Traveler, and Critic agents working together
- **Two-Phase Planning**: High-level planning followed by detailed itinerary creation
- **Interactive Planning**: Simulated conversation between agents for better planning
- **Comprehensive Output**: Detailed day-by-day itineraries with accommodations, restaurants, and activities
- **Cultural Insights**: Local recommendations and cultural tips
- **Practical Logistics**: Transportation, timing, and practical advice
- **CamelAI Framework**: Built on CamelAI's robust multi-agent architecture
- **Customizable Models**: Different AI models for different agent roles

## Prerequisites

- Python 3.8 or higher
- OpenAI API account with access to GPT-4o and GPT-4o-mini
- Internet connection for API calls

## Environment Variables

Create a `.env` file in the project directory with the following variable:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### API Key Setup

1. **OpenAI API Key**: 
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Navigate to API Keys section
   - Create a new API key with GPT-4o and GPT-4o-mini access

## Installation

1. Clone or navigate to the Trip-Planner-Agent directory:
```bash
cd Advanced-Agents/Trip-Planner-Agent
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Environment Variables section above)

## Usage

### Basic Usage

Run the agent with a travel request:
```python
from trip_planner import app

# Plan a trip
result = app("I want to plan a 5-day trip to Tokyo, Japan. I'm interested in food, culture, and technology. My budget is $2000.")
print(result)
```

### Interactive Usage

Create a custom planning session:
```python
from trip_planner import MultiAgentTravelPlanning

# Create a custom planner
travel_planner = MultiAgentTravelPlanning()

# Start planning session
itinerary = travel_planner.start_planning_session(
    initial_request="Plan a romantic weekend getaway to Paris",
    max_rounds=5
)
print(itinerary)
```

### Programmatic Integration

Use the agent in your own applications:
```python
from trip_planner import MultiAgentTravelPlanning
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType

# Custom model configuration
llm_assistant = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI, 
    model_type=ModelType.GPT_4O
)
llm_user = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI, 
    model_type=ModelType.GPT_4O_MINI
)

# Create custom planner
planner = MultiAgentTravelPlanning(
    llm_assistant=llm_assistant,
    llm_user=llm_user
)

# Generate itinerary
itinerary = planner.start_planning_session(
    initial_request="Plan a family vacation to Disney World",
    max_rounds=3
)
```

### Batch Planning

Plan multiple trips efficiently:
```python
from trip_planner import app

def plan_multiple_trips(requests: list) -> list:
    """Plan multiple trips efficiently."""
    results = []
    for request in requests:
        itinerary = app(request)
        results.append({
            'request': request,
            'itinerary': itinerary
        })
    return results

# Example usage
trip_requests = [
    "Plan a beach vacation to Bali",
    "Plan a city break to New York",
    "Plan a hiking trip to Switzerland"
]
all_itineraries = plan_multiple_trips(trip_requests)
```

## Customization

### Model Configuration

Change the AI models used for different agents:
```python
# Custom model selection
class CustomTravelPlanning(MultiAgentTravelPlanning):
    def __init__(self):
        # Use different models for different roles
        llm_assistant = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI, 
            model_type=ModelType.GPT_4O  # Best model for travel guide
        )
        llm_user = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI, 
            model_type=ModelType.GPT_4O_MINI  # Efficient model for traveler
        )
        llm_critique = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI, 
            model_type=ModelType.GPT_3_5_TURBO  # Fast model for critic
        )
        llm_organizer = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI, 
            model_type=ModelType.GPT_4O  # Best model for final organization
        )
        
        super().__init__(
            llm_assistant=llm_assistant,
            llm_user=llm_user,
            llm_critique=llm_critique,
            llm_organizer=llm_organizer
        )
```

### Agent Customization

Modify agent roles and behavior:
```python
def custom_setup_agents(self):
    """Custom agent setup with specialized roles."""
    
    # Custom travel guide
    travel_guide_sys_msg = """You are an expert travel guide specializing in luxury travel experiences.
    Focus on:
    - High-end accommodations and experiences
    - Exclusive dining recommendations
    - VIP access and special arrangements
    - Personalized service recommendations
    
    Always consider the traveler's preferences and budget constraints."""
    
    # Custom traveler
    traveler_sys_msg = """You are a sophisticated traveler with refined tastes.
    Your preferences include:
    - Luxury accommodations
    - Fine dining experiences
    - Cultural activities
    - Exclusive experiences
    
    Be specific about your preferences and provide detailed feedback."""
    
    # Custom critic
    critic_sys_msg = """You are a luxury travel critic with high standards.
    Evaluate plans based on:
    - Quality of accommodations
    - Dining excellence
    - Experience uniqueness
    - Value for money
    - Cultural authenticity"""
    
    # Set up agents with custom messages
    self.travel_guide = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Luxury Travel Guide",
            content=travel_guide_sys_msg
        ),
        model=self.llm_assistant
    )
    
    self.traveller = ChatAgent(
        system_message=BaseMessage.make_user_message(
            role_name="Luxury Traveler",
            content=traveler_sys_msg
        ),
        model=self.llm_user
    )
    
    self.critic = ChatAgent(
        system_message=BaseMessage.make_assistant_message(
            role_name="Luxury Travel Critic",
            content=critic_sys_msg
        ),
        model=self.llm_critique
    )
```

### Planning Parameters

Customize planning behavior:
```python
def custom_planning_session(self, initial_request: str, max_rounds: int = 10, 
                           planning_style: str = "detailed"):
    """Custom planning session with different styles."""
    
    if planning_style == "quick":
        # Quick planning with fewer rounds
        max_rounds = 3
        self.critic.system_message.content += "\nProvide quick, decisive feedback."
    
    elif planning_style == "detailed":
        # Detailed planning with more rounds
        max_rounds = 15
        self.critic.system_message.content += "\nProvide thorough, detailed feedback."
    
    elif planning_style == "budget":
        # Budget-focused planning
        self.travel_guide.system_message.content += "\nFocus on cost-effective options."
        self.traveller.system_message.content += "\nPrioritize value for money."
    
    return self.start_planning_session(initial_request, max_rounds)
```

### Output Format

Customize the itinerary output format:
```python
def custom_itinerary_format(self, conversation_history: List[Tuple[str, str]]) -> str:
    """Generate custom itinerary format."""
    
    organizer_request = BaseMessage.make_user_message(
        role_name="System",
        content=f"""Based on the planning discussion, create a comprehensive itinerary.

PLANNING DISCUSSION:
{self._compile_planning_summary(conversary_history)}

Create a detailed itinerary with the following sections:

## Trip Overview
- Destination summary
- Travel dates and duration
- Budget allocation

## Accommodations
- Hotel recommendations with prices
- Location benefits
- Amenities and services

## Daily Itinerary
### Day 1: [Date]
- Morning activities
- Lunch recommendations
- Afternoon activities
- Dinner recommendations
- Evening entertainment

## Transportation
- Airport transfers
- Local transportation
- Inter-city travel

## Cultural Tips
- Local customs and etiquette
- Language basics
- Safety considerations

## Budget Breakdown
- Accommodation costs
- Food and dining
- Activities and attractions
- Transportation
- Miscellaneous expenses

## Booking Information
- Recommended booking platforms
- Contact information
- Reservation tips"""
    )
    
    organizer_response = self.organizer.step(organizer_request)
    return organizer_response.msg.content
```

### Error Handling

Add robust error handling:
```python
def robust_planning_session(self, initial_request: str, max_rounds: int = 15):
    """Planning session with error handling."""
    try:
        return self.start_planning_session(initial_request, max_rounds)
    except Exception as e:
        return f"Error during planning: {str(e)}\n\nPlease try again with a different request."
```

## Advanced Features

### Specialized Planning

Add specialized planning capabilities:
```python
def business_travel_planning(self, request: str):
    """Specialized business travel planning."""
    
    # Modify agent roles for business travel
    business_guide_msg = """You are a business travel specialist.
    Focus on:
    - Business-friendly accommodations
    - Meeting and conference facilities
    - Networking opportunities
    - Efficient transportation
    - Professional dining options"""
    
    self.travel_guide.system_message.content = business_guide_msg
    
    return self.start_planning_session(request, max_rounds=10)

def adventure_travel_planning(self, request: str):
    """Specialized adventure travel planning."""
    
    # Modify agent roles for adventure travel
    adventure_guide_msg = """You are an adventure travel specialist.
    Focus on:
    - Outdoor activities and excursions
    - Adventure gear and equipment
    - Safety considerations
    - Physical fitness requirements
    - Local adventure guides and operators"""
    
    self.travel_guide.system_message.content = adventure_guide_msg
    
    return self.start_planning_session(request, max_rounds=10)
```

### Multi-Destination Planning

Plan complex multi-destination trips:
```python
def multi_destination_planning(self, destinations: list, request: str):
    """Plan trips with multiple destinations."""
    
    multi_dest_msg = f"""You are planning a multi-destination trip to: {', '.join(destinations)}.
    
    Consider:
    - Transportation between destinations
    - Optimal route planning
    - Time allocation for each destination
    - Visa and entry requirements
    - Budget distribution across destinations
    
    Original request: {request}"""
    
    return self.start_planning_session(multi_dest_msg, max_rounds=15)
```

### Seasonal Planning

Add seasonal considerations:
```python
def seasonal_planning(self, request: str, season: str):
    """Plan trips with seasonal considerations."""
    
    seasonal_msg = f"""You are planning a {season} trip.
    
    Consider {season}-specific factors:
    - Weather conditions and appropriate clothing
    - Seasonal activities and attractions
    - Peak vs. off-peak pricing
    - Seasonal closures or limited availability
    - Special seasonal events and festivals
    
    Original request: {request}"""
    
    return self.start_planning_session(seasonal_msg, max_rounds=12)
```

### Budget Optimization

Add budget optimization features:
```python
def budget_optimized_planning(self, request: str, budget: float):
    """Plan trips with budget optimization."""
    
    budget_msg = f"""You are planning a trip with a budget of ${budget}.
    
    Focus on:
    - Cost-effective accommodation options
    - Value-for-money dining experiences
    - Free and low-cost activities
    - Transportation cost optimization
    - Budget allocation across categories
    
    Original request: {request}"""
    
    return self.start_planning_session(budget_msg, max_rounds=10)
```
