from strands import Agent, tool
from strands_tools import calculator # Import the calculator tool
import argparse
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
import asyncio
from datetime import datetime

app = BedrockAgentCoreApp()

# Create a custom tool 
@tool
def weather():
    """ Get weather """ # Dummy implementation
    return "sunny"

@tool
def get_time():
    """ Get current time """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

model_id = "amazon.nova-lite-v1:0"
model = BedrockModel(
    model_id=model_id,
)
agent = Agent(
    model=model,
    tools=[
        calculator, weather, get_time
    ],
    system_prompt="""
    You're a helpful assistant. You can do simple math calculations, 
    tell the weather, and provide the current time.
    Always start by acknowledging the user's name 
    """
)

def get_user_name(user_id):
    users = {
        "1": "Maira",
        "2": "Mani",
        "3": "Mark",
        "4": "Ishan",
        "5": "Dhawal"
    }
    return users[user_id]
    
@app.entrypoint
def strands_agent_bedrock_handling_context(payload, context):
    """
    AgentCore Runtime entrypoint that demonstrates context handling and session management.
    
    Args:
        payload: The input payload containing user data and request information
        context: The runtime context object containing session and execution information
    
    Returns:
        str: The agent's response incorporating context information
    """
    user_input = payload.get("prompt")
    user_id = payload.get("user_id")
    user_name = get_user_name(user_id)
    
    # Access runtime context information
    print("=== Runtime Context Information ===")
    print("User id:", user_id)
    print("User Name:", user_name)
    print("User input:", user_input)
    print("Runtime Session ID:", context.session_id)
    print("Context Object Type:", type(context))
    print("=== End Context Information ===")
    
    # Create a personalized prompt that includes context information
    prompt = f"""My name is {user_name}. Here is my request: {user_input}
    
    Additional context: This is session {context.session_id}. 
    Please acknowledge my name and provide assistance."""
    
    response = agent(prompt)
    return response.message['content'][0]['text']

if __name__ == "__main__":
    app.run()
