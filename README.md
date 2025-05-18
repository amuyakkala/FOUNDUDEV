# FoundYou - Your AI Matchmaker for Hackathon Success! 🚀

## Abstract

Welcome to FoundYou - where AI meets human potential! 🤖❤️

FoundYou is your intelligent matchmaking companion for hackathons, designed to connect brilliant minds and create powerful partnerships. Think of it as your personal AI wingman that understands both your technical prowess and your entrepreneurial spirit.

### How It Works 🎯

1. **Smart Conversations** 💬
   - Chat with our AI guide, Synthia, who gets to know you through natural conversations
   - Share your skills, interests, and what you're looking for in a team
   - Get instant, personalized responses about the hackathon and potential opportunities

2. **Intelligent Matching** 🧠
   - Our AI analyzes your profile and chat history to understand your unique strengths
   - Matches you with complementary team members based on:
     - Technical skills and expertise
     - Project interests and goals
     - Communication style and working preferences
     - Complementary needs and shared vision

3. **Hackathon Expertise** 🏆
   - Built-in knowledge about the AGENTIC STARTUP RAGATHON
   - Real-time information about tracks, tech stack, and resources
   - Guidance on project validation and development milestones

### Why FoundYou? 🌟

- **Save Time**: No more scrolling through endless profiles or awkward networking
- **Better Matches**: AI-powered compatibility scoring ensures meaningful connections
- **Smart Guidance**: Get insights about the hackathon while finding your perfect match
- **Real-time Updates**: Stay informed about event details and opportunities

Whether you're a seasoned hacker or a first-time participant, FoundYou helps you find your ideal team and maximize your hackathon experience. Let's turn "Who should I team up with?" into "Let's build something amazing together!" 🚀

---

# FoundMatch - AI-Powered Startup Matchmaking

FoundMatch is an intelligent matchmaking platform built during the AGENTIC STARTUP RAGATHON. It uses AI to connect founders based on shared goals, complementary skills, and aligned visions.

## Features

- 🤖 AI-powered conversation and matching
- 👥 Smart founder matching algorithm
- 💬 Real-time chat interface
- 🎯 Goal and skill-based matching
- 📊 Detailed match explanations

## Tech Stack

- **Backend**: Python/Flask
- **AI Engine**: Groq's Llama 3.3 70B
- **Frontend**: HTML/CSS/JavaScript
- **Data Storage**: JSON-based
- **Authentication**: Session-based

## Prerequisites

- Python 3.8 or higher
- Git
- A Groq API key (get one at https://console.groq.com)

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/amuyakkala/FOUNDUDEV.git
cd FOUNDUDEV
```

2. Create and activate a virtual environment (recommended):
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create a .env file
touch .env

# Add your Groq API key to .env
echo "GROQ_API_KEY=your_api_key_here" > .env
```

5. Run the application:
```bash
python app.py
```

6. Visit `http://localhost:5000` in your browser

## Project Structure

```
FOUNDUDEV/
├── app.py              # Main Flask application
├── matchmaking.py      # Matching algorithm
├── user_data.py        # User management
├── system_prompt.py    # AI system prompt
├── static/            # Static assets
│   └── css/
├── templates/         # HTML templates
└── chat_history/      # User chat histories
```

## Key Components

### Chat System
- Real-time chat interface using Flask
- AI-powered responses using Groq's Llama 3.3 70B model
- Markdown formatting for rich text responses

### Matchmaking System
- AI-powered matching algorithm
- User profile generation from chat history
- Compatibility scoring and match recommendations

### User Management
- Session-based authentication
- JSON-based user data storage
- Chat history tracking

## Development

### Adding New Features
1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push to GitHub:
```bash
git push origin feature/your-feature-name
```

### Running Tests
```bash
# Add test commands here when tests are implemented
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Built during the AGENTIC STARTUP RAGATHON
- Powered by Groq's Llama 3.3 70B model
- Inspired by the need for better founder matchmaking 