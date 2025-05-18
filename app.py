from flask import Flask, render_template, request, jsonify, redirect, url_for
from user_data import UserManager
from matchmaking import find_best_match
import json
import markdown
from markupsafe import Markup
from datetime import datetime
import logging
import groq
import os
from dotenv import load_dotenv
from system_prompt import SYSTEM_PROMPT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

# Initialize Groq client
client = groq.Client(api_key=GROQ_API_KEY)

def get_ai_response(messages):
    """Get response from Groq API."""
    try:
        # Format the system prompt for the chat
        system_content = f"""You are {SYSTEM_PROMPT['systemInstruction']['name']}, with the following personality traits:
{', '.join(SYSTEM_PROMPT['systemInstruction']['personality']['traits'])}

Your tone should be:
{', '.join(SYSTEM_PROMPT['systemInstruction']['personality']['tone'])}

Your objectives are:
{', '.join(SYSTEM_PROMPT['systemInstruction']['objectives'])}

You need to gather this information:
{', '.join(SYSTEM_PROMPT['systemInstruction']['requiredInfo'])}

Keep responses concise and focused. After getting the name, ask about their purpose for attending. Don't repeat information already shared. All responses should be formatted in Markdown, using appropriate formatting for headings, lists, emphasis, and code blocks.

Event Details:
- Name: {SYSTEM_PROMPT['eventDetails']['name']}
- Dates: {SYSTEM_PROMPT['eventDetails']['dates']}
- Motto: {SYSTEM_PROMPT['eventDetails']['motto']}
- Tagline: {SYSTEM_PROMPT['eventDetails']['tagline']}
- Core Purpose: {SYSTEM_PROMPT['eventDetails']['corePurpose']}"""

        # Create a new messages array with the system message first
        formatted_messages = [
            {"role": "system", "content": system_content}
        ]

        # Add the rest of the messages
        for msg in messages:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                formatted_messages.append({
                    "role": msg['role'],
                    "content": str(msg['content'])
                })

        response = client.chat.completions.create(
            model=SYSTEM_PROMPT['runSettings']['model'],
            messages=formatted_messages,
            temperature=SYSTEM_PROMPT['runSettings']['temperature'],
            top_p=SYSTEM_PROMPT['runSettings']['topP'],
            max_tokens=SYSTEM_PROMPT['runSettings']['maxOutputTokens']
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return None

app = Flask(__name__)
user_manager = UserManager()

@app.route('/')
def home():
    """Render the home page with active users."""
    try:
        users = user_manager.get_active_users(minutes=30)
        
        # Create the initial welcome message with Markdown
        welcome_message = SYSTEM_PROMPT['systemInstruction']['openingLine']
        
        # Convert Markdown to HTML
        welcome_html = markdown.markdown(
            welcome_message,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists',
                'markdown.extensions.codehilite'
            ]
        )
        
        return render_template('index.html', users=users, welcome_message=welcome_html)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        return render_template('error.html', error="An error occurred. Please try again.")

@app.route('/login')
def login_page():
    """Render the login page."""
    return render_template('login.html')

@app.route('/users', methods=['GET'])
def get_users():
    """Get list of all users and available matches count."""
    try:
        users = user_manager.get_all_users()
        current_user = request.args.get('user_name')
        
        # Convert list of users to dictionary for easier processing
        users_dict = {user['name']: user for user in users}
        
        # Filter out current user and count eligible matches
        eligible_matches = {
            name: data for name, data in users_dict.items()
            if data['conversation_count'] >= 3 and name != current_user
        }
        
        # Add available matches count to response
        response = {
            'users': [
                {
                    'name': name,
                    'conversation_count': data['conversation_count'],
                    'last_active': data.get('last_active', '')
                }
                for name, data in users_dict.items()
            ],
            'available_matches': len(eligible_matches)
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in get_users route: {str(e)}")
        return jsonify({"error": "Failed to get users"}), 500

@app.route('/login', methods=['POST'])
def login():
    """Handle user login/registration."""
    try:
        data = request.json
        name = data.get('name', '').strip()
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
            
        # Create or get user
        user = user_manager.create_user(name)
        
        # Get user's chat history
        chat_history = user_manager.get_chat_history(name)
        
        # If this is a new user or no chat history exists, add the name introduction
        if not chat_history:
            intro_message = f"I'm {name}"
            user_manager.add_chat_history(
                name,
                intro_message,
                "Great to meet you! I'm Synthia, your AI guide for the AGENTIC STARTUP RAGATHON. I'd love to learn more about your background and what brings you here today."
            )
            chat_history = user_manager.get_chat_history(name)
        
        return jsonify({
            "user": {
                "name": user["name"],
                "conversation_count": user["conversation_count"],
                "last_active": user.get("last_active", "")
            },
            "chat_history": chat_history
        })
    except Exception as e:
        logger.error(f"Error in login route: {str(e)}")
        return jsonify({"error": "Login failed"}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        user_name = request.json.get('user_name')
        if not user_name:
            return jsonify({"error": "User name is required"}), 400
            
        user_message = request.json.get('message', '')
        
        if not user_message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Initialize messages with system prompt
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
        # Get chat history and add to messages
        chat_history = user_manager.get_chat_history(user_name)
        if chat_history:
            for msg in chat_history:
                if isinstance(msg, dict) and 'user' in msg and 'bot' in msg:
                    messages.append({"role": "user", "content": msg['user']})
                    messages.append({"role": "assistant", "content": msg['bot']})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        ai_response = get_ai_response(messages)
        if not ai_response:
            return jsonify({"error": "Failed to get AI response"}), 500
        
        # Convert Markdown to HTML
        html_response = markdown.markdown(
            ai_response,
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists',
                'markdown.extensions.codehilite'
            ]
        )
        
        # Save chat history
        user_manager.add_chat_history(user_name, user_message, ai_response)
        
        return jsonify({
            "response": {
                "text": ai_response,
                "html_response": html_response
            }
        })
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/match', methods=['POST'])
def find_match():
    """Handle matchmaking request."""
    try:
        user_name = request.json.get('user_name')
        if not user_name:
            return jsonify({"error": "User name is required"}), 400
            
        logger.info(f"Finding match for user: {user_name}")
        
        user = user_manager.get_user(user_name)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check if user has enough conversation history
        if user['conversation_count'] < 3:
            return jsonify({
                "error": "Not enough conversation history",
                "required_messages": 3,
                "current_messages": user['conversation_count']
            }), 400
        
        # Get all users and their chat histories
        all_users = user_manager.get_all_users()
        logger.info(f"Total users: {len(all_users)}")
        
        # Convert list of users to dictionary for easier processing
        users_dict = {user['name']: user for user in all_users}
        
        # Add chat history to each user's data
        for name in users_dict:
            users_dict[name]['chat_history'] = user_manager.get_chat_history(name)
        
        # Filter users who have enough conversation history
        eligible_users = {
            name: data for name, data in users_dict.items()
            if data['conversation_count'] >= 3 and name != user_name
        }
        logger.info(f"Eligible users: {len(eligible_users)}")
        
        if not eligible_users:
            return jsonify({
                "error": "No eligible matches found",
                "message": "No other users have completed enough conversations yet."
            }), 404
        
        # Find the best match
        match_result = find_best_match(user_name, eligible_users)
        logger.info(f"Match found: {match_result}")
        
        # Convert match explanation to HTML
        html_response = markdown.markdown(
            match_result['explanation'],
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.tables',
                'markdown.extensions.nl2br',
                'markdown.extensions.sane_lists',
                'markdown.extensions.codehilite'
            ]
        )
        
        return jsonify({
            "match": match_result['match'],
            "explanation": match_result['explanation'],
            "html_explanation": html_response,
            "score": match_result.get('score', 0)
        })
    except Exception as e:
        logger.error(f"Error in matchmaking: {str(e)}")
        return jsonify({
            "error": "Error finding match",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True) 