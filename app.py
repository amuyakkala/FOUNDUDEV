from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=1.0,
            top_p=0.95,
            max_tokens=32768
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return None

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management
user_manager = UserManager()

# Initialize conversation history with a proper system prompt
messages = [
    {
        "role": "system",
        "content": """You are Synthia, a friendly and concise AI guide for the AGENTIC STARTUP RAGATHON. Keep your responses short, engaging, and to the point.

Key Points:
- Be brief and conversational
- Use emojis sparingly but effectively
- Keep responses under 3-4 sentences when possible
- Focus on one topic at a time
- Use simple, clear language
- Avoid unnecessary formatting or markdown unless specifically needed

Your main goals:
1. Help users connect with others
2. Guide them through the event
3. Answer questions directly
4. Keep the conversation flowing naturally

Remember: Less is more. Users prefer quick, helpful responses over lengthy explanations."""
    }
]

@app.route('/')
def home():
    """Render the home page with active users."""
    try:
        # Check if user is logged in
        if 'user_name' not in session:
            return redirect(url_for('login'))
            
        users = user_manager.get_active_users(minutes=30)
        
        # Create the initial welcome message with Markdown
        welcome_message = """👋 **Welcome to the AGENTIC STARTUP RAGATHON!** I'm Synthia, your AI guide for this exciting event. 

### Let's Get Started
I'm here to help you make the most of this experience and connect with amazing people. 

**What's your name?** I'd love to get to know you better! 🚀"""
        
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
        current_user = session.get('user_name')
        
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
        session['user_name'] = name
        
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
        if 'user_name' not in session:
            return jsonify({"error": "Not logged in"}), 401
            
        user_name = session['user_name']
        user_message = request.json.get('message', '')
        
        if not user_message.strip():
            return jsonify({"error": "Message cannot be empty"}), 400
        
        # Add user message to history
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        ai_response = get_ai_response(messages)
        if not ai_response:
            ai_response = "I apologize, but I'm having trouble processing your request. Could you please try again?"
        
        # Add AI response to history
        messages.append({"role": "assistant", "content": ai_response})
        
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
        
        # Save chat history with both raw Markdown and HTML versions
        user_manager.add_chat_history(user_name, user_message, ai_response)
        
        return jsonify({
            "response": {
                "text": ai_response,
                "html_response": html_response
            }
        })
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}")
        return jsonify({"error": "Failed to process message"}), 500

@app.route('/match', methods=['POST'])
def find_match():
    """Handle matchmaking request."""
    try:
        if 'user_name' not in session:
            return jsonify({"error": "Not logged in"}), 401
            
        user_name = session['user_name']
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