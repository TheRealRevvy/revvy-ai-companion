# Add unit awareness to the AI Engine

def _build_prompt(self, query, context=None):
    """Build a prompt with context and conversation history"""
    # Get personality traits
    personality_traits = self._get_personality_traits()
    
    # Get unit system
    unit_system = self.config.get("display", "unit_system", "metric")
    
    # Start with system prompt
    prompt = f"""You are {self.current_personality}, an AI assistant for vehicles. 
{personality_traits}

Current Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Using {unit_system.capitalize()} Units
"""
    
    # Rest of the method remains the same
    # ...