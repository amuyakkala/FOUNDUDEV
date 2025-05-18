from typing import List, Dict
import json
import groq
import os
from dotenv import load_dotenv
from user_data import UserManager

# Load environment variables
load_dotenv()

# Initialize Groq client and UserManager
client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))
user_manager = UserManager()

# Prompt for generating user summaries
USER_SUMMARY_PROMPT = """Based on the following conversation history, create a comprehensive summary of the user's profile. Focus on:

1. Technical skills and expertise
2. Project interests and goals
3. Communication style and personality
4. Working style and preferences
5. Areas where they could use complementary skills

Format your response in clear, structured markdown that highlights key attributes relevant for team matching.

Conversation History:
{conversation_history}"""

# Prompt for finding the best match
MATCHING_PROMPT = """You are an expert at matching hackathon participants based on their profiles. Your goal is to find the perfect match that would lead to the most successful and enjoyable hackathon experience.

Current User Profile:
{current_user_summary}

Available Matches:
{available_matches}

Please analyze these profiles and find the best match for the current user. Consider:
1. Complementary skills and expertise
2. Compatible working styles
3. Shared interests and goals
4. Potential for successful collaboration
5. Overall team dynamic

Format your response in markdown with the following sections:
## Best Match
[Name of the best match]

## Match Score
[Score between 0 and 1]

## Why This Match Works
[Detailed explanation of why this is a good match]

## Shared Interests & Skills
[List of shared interests and complementary skills]

## Potential Collaboration Areas
[Specific project ideas or areas where they could collaborate]

## Next Steps
[Suggested next steps for the matched users]"""

def generate_user_summary(conversation_history: List[Dict]) -> str:
    """Generate a summary of a user based on their conversation history."""
    if not conversation_history:
        print("Warning: Empty conversation history")
        return "No conversation history available."
    
    # Format conversation history for the prompt
    formatted_history = []
    for msg in conversation_history:
        if not isinstance(msg, dict) or 'user' not in msg or 'bot' not in msg:
            print(f"Warning: Invalid message format: {msg}")
            continue
            
        user_msg = msg['user'].strip()
        bot_msg = msg['bot'].strip()
        if user_msg and bot_msg:  # Only include non-empty messages
            formatted_history.append(f"User: {user_msg}")
            formatted_history.append(f"Assistant: {bot_msg}")
    
    if not formatted_history:
        print("Warning: No valid messages in conversation history")
        return "No valid messages in conversation history."
    
    conversation_text = "\n".join(formatted_history)
    print("\n=== Formatted Conversation History ===")
    print(conversation_text)
    print("=====================================\n")
    
    try:
        # Create messages with system instruction
        messages = [
            {
                "role": "system",
                "content": "You are an expert at analyzing conversations and creating comprehensive user profiles. Format your response in clear, structured markdown."
            },
            {
                "role": "user",
                "content": USER_SUMMARY_PROMPT.format(conversation_history=conversation_text)
            }
        ]
        
        print("\n=== User Summary Request ===")
        print("System Message:", messages[0]["content"])
        print("\nUser Message:", messages[1]["content"])
        print("===========================\n")
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Get the response content
        content = response.choices[0].message.content.strip()
        print("\n=== User Summary Response ===")
        print(content)
        print("===========================\n")
        
        return content
    except Exception as e:
        error_msg = str(e)
        if "rate_limit_exceeded" in error_msg:
            print(f"Rate limit exceeded: {error_msg}")
            return "Rate limit exceeded. Please try again in about an hour."
        print(f"Error generating user summary: {e}")
        return "Error generating user summary."

def find_best_match(current_user: str, eligible_users: Dict) -> Dict:
    """Find the best match for a user among all available users."""
    try:
        print(f"\n=== Finding match for {current_user} ===")
        # Get current user's chat history from the user manager
        current_user_history = user_manager.get_chat_history(current_user)
        print(f"Current user history length: {len(current_user_history)} messages")
        
        current_user_summary = generate_user_summary(current_user_history)
        if "Rate limit exceeded" in current_user_summary:
            return {
                "match": None,
                "explanation": "We've reached our daily limit for AI processing. Please try again in about an hour.",
                "score": 0
            }
        print("\nCurrent user summary:", current_user_summary)
        
        # Generate summaries for all other users
        available_matches = []
        for name, data in eligible_users.items():
            if name == current_user:
                continue
                
            chat_history = data.get('chat_history', [])
            if not chat_history:
                continue
                
            print(f"\nGenerating summary for {name}")
            user_summary = generate_user_summary(chat_history)
            if "Rate limit exceeded" in user_summary:
                return {
                    "match": None,
                    "explanation": "We've reached our daily limit for AI processing. Please try again in about an hour.",
                    "score": 0
                }
            available_matches.append({
                "name": name,
                "summary": user_summary
            })
        
        if not available_matches:
            print("No available matches found")
            return {
                "match": None,
                "explanation": "No suitable matches found at this time. Keep chatting to find potential matches!",
                "score": 0
            }
        
        # Format available matches for the prompt
        formatted_matches = "\n".join([
            f"User: {match['name']}\nProfile: {match['summary']}"
            for match in available_matches
        ])
        
        # Create messages with system instruction
        messages = [
            {
                "role": "system",
                "content": "You are an expert at matching hackathon participants. Format your response in clear, structured markdown."
            },
            {
                "role": "user",
                "content": MATCHING_PROMPT.format(
                    current_user_summary=current_user_summary,
                    available_matches=formatted_matches
                )
            }
        ]
        
        print("\n=== Match Request ===")
        print("System Message:", messages[0]["content"])
        print("\nUser Message:", messages[1]["content"])
        print("====================\n")
        
        # Get match recommendation from Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Get the response content
        content = response.choices[0].message.content.strip()
        print("\n=== Match Response ===")
        print(content)
        print("====================\n")
        
        # Extract match name and score from markdown
        match_name = None
        match_score = 0.0
        
        # Look for match name in the response
        match_section = content.split("## Best Match")[1].split("##")[0] if "## Best Match" in content else ""
        if match_section:
            match_name = match_section.strip()
        
        # Look for match score in the response
        score_section = content.split("## Match Score")[1].split("##")[0] if "## Match Score" in content else ""
        if score_section:
            try:
                score_text = score_section.strip()
                # Extract first number between 0 and 1
                import re
                score_match = re.search(r'0\.\d+', score_text)
                if score_match:
                    match_score = float(score_match.group())
            except:
                pass
        
        return {
            "match": match_name,
            "explanation": content,  # Return the full markdown response
            "score": match_score
        }
    except Exception as e:
        error_msg = str(e)
        if "rate_limit_exceeded" in error_msg:
            print(f"Rate limit exceeded: {error_msg}")
            return {
                "match": None,
                "explanation": "We've reached our daily limit for AI processing. Please try again in about an hour.",
                "score": 0
            }
        print(f"Error finding best match: {e}")
        return {
            "match": None,
            "explanation": "An error occurred while finding matches. Please try again.",
            "score": 0
        } 