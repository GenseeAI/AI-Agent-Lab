from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.types import ModelPlatformType, ModelType, RoleType
from camel.generators import SystemMessageGenerator
from typing import List, Tuple

class MultiAgentTravelPlanning:
    def __init__(self, llm_assistant=None, llm_user=None, llm_critique=None, llm_organizer=None):
        # Initialize models
        if not llm_assistant:
            self.llm_assistant = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI, 
                model_type=ModelType.GPT_4O
            )
        else:
            self.llm_assistant = llm_assistant

        if not llm_user:
            self.llm_user = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI, 
                model_type=ModelType.GPT_4O_MINI
            )
        else:
            self.llm_user = llm_user
            
        if not llm_critique:
            self.llm_critique = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI, 
                model_type=ModelType.GPT_4O_MINI
            )
        else:
            self.llm_critique = llm_critique
            
        if not llm_organizer:
            self.llm_organizer = ModelFactory.create(
                model_platform=ModelPlatformType.OPENAI, 
                model_type=ModelType.GPT_4O
            )
        else:
            self.llm_organizer = llm_organizer
        
        # Initialize agents
        self._setup_agents()
        
    def _setup_agents(self):
        task_prompt = """You are coordinating a travel planning session. 
        The goal is to develop an in-depth travel plan including where to visit, 
        where to stay, and what to eat for a specific destination.""" 

        sys_msg_gen = SystemMessageGenerator()
        
        travel_guide_sys_msg = sys_msg_gen.from_dict(
            meta_dict={
                'assistant_role': 'An experienced travel guide',
                'user_role': 'Traveller', 
                'task': task_prompt,
                'criteria': 'Provide detailed, practical travel recommendations based on the traveller\'s preferences'
            },
            role_tuple=('An experienced travel guide', RoleType.ASSISTANT)
        )
        
        travel_guide_sys_msg.content = """You are an experienced travel guide who specializes in creating comprehensive travel plans.
Your role is to:
- Ask clarifying questions about the traveller's preferences, budget, and interests
- Provide detailed recommendations for destinations, accommodations, restaurants, and activities
- Consider practical aspects like transportation, timing, and logistics
- Be responsive to feedback and adapt your recommendations
- Focus on high-level planning and expert advice

Work collaboratively with the traveller and respond thoughtfully to any critic feedback to improve your recommendations.
Keep your responses focused and avoid overwhelming detail - the Itinerary Organizer will handle the detailed structuring later."""
 
        traveller_sys_msg = sys_msg_gen.from_dict(
            meta_dict={
                'user_role': 'Traveller',
                'assistant_role': 'An experienced travel guide',
                'task': task_prompt,
                'criteria': 'Provide your travel preferences and feedback on recommendations'
            },
            role_tuple=('Traveller', RoleType.USER)
        )
        
        traveller_sys_msg.content = """You are a traveller looking to plan a trip.
Your role is to:
- Share your travel preferences, budget, and interests
- Ask questions about recommendations you don't understand
- Provide feedback on suggested itineraries
- Be specific about what you like or don't like about proposals
- Help refine the travel plan based on your needs
- Indicate when you're satisfied with the general plan direction

Be an engaged participant who helps create the best possible travel experience."""

        critic_sys_msg = sys_msg_gen.from_dict(
            meta_dict={
                'critic_role': 'A picky travel critic',
                'user_role': 'Traveller',
                'assistant_role': 'An experienced travel guide', 
                'task': task_prompt,
                'criteria': 'Pick out inconsistencies in the plan. Request more details if needed to create a more comprehensive travel plan.'
            },
            role_tuple=('A picky travel critic', RoleType.CRITIC)
        )
        
        critic_sys_msg.content = """You are a picky travel critic who evaluates travel plans for completeness and quality.
Your role is to:
- Identify inconsistencies, gaps, or unrealistic aspects in travel proposals
- Request more specific details when plans are too vague
- Point out missing essential information (budget considerations, timing issues, logistics)
- Ensure recommendations match the traveller's stated preferences
- Suggest improvements to make the plan more comprehensive and practical

When the high-level plan seems solid and the traveller appears satisfied, say "READY_FOR_DETAILED_ITINERARY" to move to the detailed planning phase."""

        organizer_sys_msg = sys_msg_gen.from_dict(
            meta_dict={
                'role': 'Professional itinerary organizer',
                'task': task_prompt,
                'criteria': 'Create detailed, researched, day-by-day travel itineraries'
            },
            role_tuple=('Professional itinerary organizer', RoleType.ASSISTANT)
        )
        
        organizer_sys_msg.content = """You are a professional itinerary organizer who creates detailed, well-researched travel plans.
Your role is to:
- Create a detailed day-by-day itinerary based on the travel discussion
- Include suggested accommodations, restaurants, attractions, and activities
- Organize transportation and timing recommendations
- Structure everything in a clear, easy-to-follow format
- Provide practical tips and cultural insights
- Use your extensive knowledge of destinations to provide comprehensive recommendations

Create a complete, ready-to-use travel itinerary that travelers can follow."""

        self.travel_guide = ChatAgent(
            system_message=travel_guide_sys_msg,
            model=self.llm_assistant
        )
        
        self.traveller = ChatAgent(
            system_message=traveller_sys_msg,
            model=self.llm_user
        )
        
        self.critic = ChatAgent(
            system_message=critic_sys_msg,
            model=self.llm_critique
        )
        
        self.organizer = ChatAgent(
            system_message=organizer_sys_msg,
            model=self.llm_organizer
        )
        
    def start_planning_session(self, initial_request: str, max_rounds: int = 15):
        # Phase 1: High-level planning (silent)
        conversation_history = self._phase_1_planning(initial_request, max_rounds)
        
        # Phase 2: Create final detailed itinerary
        if conversation_history:
            final_itinerary = self._phase_2_detailed_itinerary(conversation_history)
            return final_itinerary
        
        return None
        
    def _phase_1_planning(self, initial_request: str, max_rounds: int) -> List[Tuple[str, str]]:
        current_message = BaseMessage.make_user_message(
            role_name="Traveller",
            content=initial_request
        )
        
        conversation_history = []
        round_count = 0
        
        while round_count < max_rounds:
            round_count += 1
            
            # Travel Guide Response
            guide_response = self.travel_guide.step(current_message)
            conversation_history.append(("Travel Guide", guide_response.msg.content))
            
            if guide_response.terminated:
                break

            # Traveller Response
            traveller_response = self.traveller.step(guide_response.msg)
            conversation_history.append(("Traveller", traveller_response.msg.content))
            
            if traveller_response.terminated:
                break

            # Critic Evaluation
            context_msg = BaseMessage.make_user_message(
                role_name="System",
                content=f"""Recent exchange:
                
Travel Guide: {guide_response.msg.content}

Traveller: {traveller_response.msg.content}

Please evaluate this exchange and the overall travel planning progress."""
            )
            
            critic_response = self.critic.step(context_msg)
            conversation_history.append(("Critic", critic_response.msg.content))
            
            if "READY_FOR_DETAILED_ITINERARY" in critic_response.msg.content:
                break

            if critic_response.terminated:
                break

            current_message = critic_response.msg
                
        return conversation_history
    
    def _phase_2_detailed_itinerary(self, conversation_history: List[Tuple[str, str]]) -> str:
        planning_summary = self._compile_planning_summary(conversation_history)
        
        organizer_request = BaseMessage.make_user_message(
            role_name="System",
            content=f"""Based on the following travel planning discussion, please create a complete detailed itinerary.

PLANNING DISCUSSION SUMMARY:
{planning_summary}

Create a comprehensive day-by-day itinerary that includes:
- Destination overview and what makes it special
- Suggested accommodations (types/areas, not specific hotels)
- Restaurant recommendations for authentic local cuisine
- Major attractions and cultural sites to visit
- Transportation suggestions between locations
- Timing and logistics for each day
- Cultural tips and practical advice

Focus on creating a well-organized, practical travel plan that captures the essence of the destination."""
        )
        
        # Get the final itinerary from organizer
        organizer_response = self.organizer.step(organizer_request)
        return organizer_response.msg.content
    
    def _compile_planning_summary(self, conversation_history: List[Tuple[str, str]]) -> str:
        summary_parts = []
        for i, (agent, message) in enumerate(conversation_history, 1):
            summary_parts.append(f"{i}. {agent}:\n{message}\n")
        return "\n".join(summary_parts)

def app(input_question: str):
    llm_assistant = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4_1)
    llm_user = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4_1)
    llm_critique = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4_1)
    llm_organizer = ModelFactory.create(model_platform=ModelPlatformType.OPENAI, model_type=ModelType.GPT_4_1)
    
    travel_planner = MultiAgentTravelPlanning(
        llm_assistant=llm_assistant, 
        llm_user=llm_user, 
        llm_critique=llm_critique, 
        llm_organizer=llm_organizer
    )
    
    itinerary = travel_planner.start_planning_session(
        initial_request=input_question,
        max_rounds=2
    )
    
    return itinerary