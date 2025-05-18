import groq
import json
import os
from dotenv import load_dotenv
from system_prompt import SYSTEM_PROMPT

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = groq.Client(api_key=GROQ_API_KEY)

def parse_profile(text: str) -> dict:
    """Parse a profile from natural language input using the system prompt context."""
    prompt = f"""You are {SYSTEM_PROMPT['systemInstruction']['name']}, analyzing user input to extract profile information.

Extract a user profile from this text. Return a JSON object with these fields:
- name: First name only (REQUIRED - extract from text or use "Unknown" if not found)
- purpose: Why they're attending (from {SYSTEM_PROMPT['eventDetails']['targetAudience']})
- project: What they're building (should align with {SYSTEM_PROMPT['eventDetails']['tracks']})
- looking_for: Who they want to meet
- tech_interest: List of technologies/interests (should include {', '.join(SYSTEM_PROMPT['eventDetails']['techStack'].keys())} if relevant)
- intent: Their primary goal (cofound, team up, mentor, learn, explore)
- linkedin: Their LinkedIn URL (if mentioned)

Text: {text}

Return ONLY the JSON object, no other text. If a field is not mentioned, use an empty string or empty list as appropriate.
"""
    try:
        response = client.chat.completions.create(
            model=SYSTEM_PROMPT["runSettings"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=SYSTEM_PROMPT["runSettings"]["temperature"],
            top_p=SYSTEM_PROMPT["runSettings"]["topP"],
            max_tokens=SYSTEM_PROMPT["runSettings"]["maxOutputTokens"]
        )
        
        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return {"name": "Unknown"}
        
        # Ensure tech_interest is a list
        if "tech_interest" in result:
            if isinstance(result["tech_interest"], str):
                result["tech_interest"] = [result["tech_interest"]]
        
        # Ensure name is present
        if "name" not in result or not result["name"]:
            result["name"] = "Unknown"
            
        return result
    except Exception as e:
        print(f"Error parsing profile: {e}")
        return {"name": "Unknown"}  # Return at least name field on error

def parse_field(field: str, user_reply: str) -> dict:
    """Parse a single field from user input using the system prompt context."""
    prompt = f"""You are {SYSTEM_PROMPT['systemInstruction']['name']}, analyzing user input for a specific field.

Field to extract: {field}

Context about the field:
- If 'purpose': Should align with {SYSTEM_PROMPT['eventDetails']['targetAudience']}
- If 'project': Should align with {SYSTEM_PROMPT['eventDetails']['tracks']}
- If 'tech_interest': Should include {', '.join(SYSTEM_PROMPT['eventDetails']['techStack'].keys())} if relevant

User input: {user_reply}

Return a JSON object with just the {field} field. If the input is invalid or empty, return an empty object {{}}.
"""
    try:
        response = client.chat.completions.create(
            model=SYSTEM_PROMPT["runSettings"]["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=SYSTEM_PROMPT["runSettings"]["temperature"],
            top_p=SYSTEM_PROMPT["runSettings"]["topP"],
            max_tokens=SYSTEM_PROMPT["runSettings"]["maxOutputTokens"]
        )
        
        # Parse the response
        try:
            result = json.loads(response.choices[0].message.content.strip())
            return result
        except json.JSONDecodeError:
            return {}
    except Exception as e:
        print(f"Error parsing field: {e}")
        return {} 