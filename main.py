from toolhouse import Agent
from tools.intent_tools import parse_profile, parse_field

agent = Agent(
    tools=[parse_profile, parse_field],
    instructions="You help users generate structured networking profiles using LLMs. Fill in missing info with follow-up."
) 