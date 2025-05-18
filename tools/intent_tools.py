import groq
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def parse_profile(text: str) -> dict:
    prompt = f"""
You are an onboarding assistant. Extract the following fields from the user's input and return them as a JSON object:

- purpose: Why they're attending
- project: What they're building
- looking_for: Who they want to meet
- tech_interest: A list of relevant tools, tech, or domains
- intent: What kind of collaboration they seek (e.g., cofound, mentor, explore)
- linkedin: Their LinkedIn URL if given

User message:
{text}

Return only a clean JSON object with all the above fields filled in, like this:

{{
  "purpose": "...",
  "project": "...",
  "looking_for": "...",
  "tech_interest": ["...", "..."],
  "intent": "...",
  "linkedin": "..."
}}

Be concise, structured, and never include explanations or text outside the JSON. If the user doesn't give LinkedIn, just return an empty string.
"""

    client = groq.Client(api_key=os.getenv("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"))
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    # Debugging: Print the raw response
    print("Raw API Response:", response.choices[0].message.content)

    return json.loads(response.choices[0].message.content)

def parse_field(field: str, user_reply: str) -> dict:
    prompt = f"""
You are extracting a single field: "{field}" from this user message:

\"\"\"{user_reply}\"\"\"

Return ONLY valid JSON like:
{{ "{field}": "..." }}

If the message is empty or unclear, return:
{{ "{field}": "" }}
"""

    client = groq.Client(api_key=os.getenv("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"))
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content.strip()

    # Fallback if empty
    if not content:
        print(f"⚠️ LLM returned empty for field '{field}', defaulting to empty string.")
        return {field: ""}

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        print(f"❌ LLM response was invalid JSON for field '{field}':\n{content}")
        return {field: ""} 