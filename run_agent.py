import json
import os
from tools.intent_tools import parse_profile, parse_field
import groq

QUESTION_MAP = {
    "purpose": "Why are you attending?",
    "project": "What are you building?",
    "looking_for": "Who do you want to meet?",
    "tech_interest": "What tools, tech, or domains interest you? (Enter multiple, separated by commas)",
    "intent": "What kind of collaboration are you seeking? (e.g., cofound, mentor, explore)",
    "linkedin": "What's your LinkedIn URL?"
}

# Define required fields
REQUIRED_FIELDS = ["purpose", "project", "looking_for", "tech_interest", "intent", "linkedin"]

def is_field_valid(field: str, value: any) -> bool:
    """Check if a field has a valid non-empty value."""
    if field == "tech_interest":
        if isinstance(value, str):
            # Convert comma-separated string to list
            value = [v.strip() for v in value.split(",") if v.strip()]
        return isinstance(value, list) and len(value) > 0
    return bool(value and str(value).strip())

def validate_profile(profile: dict) -> list:
    """Return list of fields that need to be filled out."""
    missing = []
    
    # Validate all required fields
    for field in REQUIRED_FIELDS:
        value = profile.get(field)
        if not is_field_valid(field, value):
            missing.append(field)
            
    return missing

def get_user_input(prompt: str) -> str:
    """Get and clean user input."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
        exit(0)

def show_progress(missing: list) -> None:
    """Show progress percentage and remaining fields."""
    total = len(REQUIRED_FIELDS)
    completed = total - len(missing)
    percentage = (completed / total) * 100
    
    print(f"\n📊 Progress: {completed}/{total} ({percentage:.0f}%) complete")
    if missing:
        print(f"📝 Still need: {', '.join(missing)}")

def save_profile(profile: dict, file: str = "profiles.json") -> None:
    """Save profile to JSON file."""
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump([], f)

    with open(file, "r") as f:
        profiles = json.load(f)

    profiles.append(profile)

    with open(file, "w") as f:
        json.dump(profiles, f, indent=2)

def score_match(p1: dict, p2: dict) -> int:
    """Calculate match score between two profiles."""
    score = 0
    # Intent matching
    if p1["intent"].lower() in p2.get("looking_for", "").lower():
        score += 1
    # Tech interest overlap
    score += len(set(p1["tech_interest"]) & set(p2["tech_interest"]))
    return score

def explain_match(p1: dict, p2: dict) -> str:
    """Use Groq to explain why these profiles match."""
    client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""
You are a matchmaking assistant. Explain why these two profiles would be a good match:

Profile 1:
- Project: {p1['project']}
- Looking for: {p1['looking_for']}
- Tech interests: {', '.join(p1['tech_interest'])}
- Intent: {p1['intent']}

Profile 2:
- Project: {p2['project']}
- Looking for: {p2['looking_for']}
- Tech interests: {', '.join(p2['tech_interest'])}
- Intent: {p2['intent']}

Common interests: {', '.join(set(p1['tech_interest']) & set(p2['tech_interest']))}

Explain in 2-3 sentences why they would be a good match, focusing on:
1. Complementary skills/needs
2. Shared interests
3. Potential collaboration value

Keep it concise and professional.
"""

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content.strip()

def find_matches(target: dict, file: str = "profiles.json") -> list:
    """Find top 3 matches for a profile."""
    if not os.path.exists(file):
        return []
        
    with open(file) as f:
        profiles = json.load(f)
        
    matches = []
    for p in profiles:
        if p != target:  # Don't match with self
            matches.append((p, score_match(target, p)))
            
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches[:3]

def run_agent():
    print("\n👋 Welcome! Let's get to know you better.")
    print("Tell me about yourself and what brings you here:")
    
    user_input = get_user_input("👉 ")
    profile = parse_profile(user_input)
    
    # Validate and collect missing fields
    missing = validate_profile(profile)
    
    MAX_RETRIES = 2
    
    while missing:
        field = missing[0]
        attempts = 0
        value = ""
        
        while attempts < MAX_RETRIES:
            print(f"\n🔁 {QUESTION_MAP[field]}")
            follow_up = get_user_input("👉 ")
            
            if not follow_up:
                print("Please provide a response.")
                attempts += 1
                continue
                
            try:
                patch = parse_field(field, follow_up)
                value = patch.get(field, "")
                
                if is_field_valid(field, value):
                    break
            except Exception as e:
                print(f"Error processing response: {str(e)}")
                value = ""
                
            attempts += 1
            if attempts < MAX_RETRIES:
                print("Please provide a valid response.")
            
        # Set the field value
        profile[field] = value
        missing = validate_profile(profile)
        
        # Show progress
        show_progress(missing)
    
    print("\n✨ Profile complete!")
    print(json.dumps(profile, indent=2))
    
    # ----------------------------
    # Step 2: Save & Match Logic
    # ----------------------------
    
    # Find matches before saving (to avoid self-matching)
    matches = find_matches(profile)
    
    if matches:
        print("\n🎯 Top 3 Matches:\n")
        for match, score in matches:
            print("🔗 LinkedIn:", match.get("linkedin", "N/A"))
            print("🛠 Project:", match.get("project", "N/A"))
            print("💬 Common Interests:", list(set(match["tech_interest"]) & set(profile["tech_interest"])))
            print("📈 Match Score:", score)
            
            # Explain the match
            try:
                explanation = explain_match(profile, match)
                print("\n💡 Why this match:", explanation)
            except Exception as e:
                print("\n💡 Match explanation unavailable:", str(e))
                
            print("-" * 40)
    else:
        print("\n🌟 You're the first profile! More matches will appear as others join.")
    
    # Save the current profile
    save_profile(profile)
    print("\n✅ Profile saved successfully!")

if __name__ == "__main__":
    run_agent() 