# FoundU - AI-Powered Networking Matchmaker

FoundU is an intelligent networking platform that helps people find the right connections at events. It uses AI to understand user profiles and match them with compatible people based on their projects, interests, and collaboration goals.

## Features

- 🤖 AI-powered profile parsing
- 🎯 Smart matching algorithm
- 💡 Match explanations
- 📊 Progress tracking
- 💾 Profile persistence

## Setup

1. Clone the repository:
```bash
git clone https://github.com/amuyakkala/FoundU.git
cd FoundU
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Add your GROQ_API_KEY to .env
```

4. Run the agent:
```bash
python run_agent.py
```

## How It Works

1. Users describe themselves and their goals
2. AI parses their input into structured profiles
3. System finds matches based on:
   - Complementary skills/needs
   - Shared tech interests
   - Collaboration intent
4. AI explains why each match would work well
5. Profiles are saved for future matching

## Tech Stack

- Python 3.12+
- Groq LLM API
- JSON for data storage
- (Coming soon) Streamlit UI

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License 