from typing import List, Dict
import json

# Prompt for generating user summaries
USER_SUMMARY_PROMPT = """Based on the following conversation history, create a comprehensive summary of the user's:
1. Technical skills and experience
2. Project interests and goals
3. Communication style and personality
4. Preferred working style
5. Areas where they could use complementary skills

Format the summary in a clear, structured way that highlights key attributes that would be relevant for team matching.

Conversation History:
{conversation_history}
"""

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

Output your match recommendation in the following format:
## Match Recommendation
**Best Match:** [Name]

### Why This Match Works
[Detailed explanation of why this is the perfect match, highlighting complementary skills and potential for success]

### Team Strengths
- [Key strength 1]
- [Key strength 2]
- [Key strength 3]

### Potential Project Directions
- [Project idea 1]
- [Project idea 2]
"""

def generate_user_summary(conversation_history: List[Dict]) -> str:
    """Generate a summary of a user based on their conversation history."""
    # Format conversation history for the prompt
    formatted_history = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in conversation_history
    ])
    
    # TODO: Call LLM with USER_SUMMARY_PROMPT
    # For now, return a placeholder
    return "User summary placeholder"

def find_best_match(current_user: str, eligible_users: Dict) -> Dict:
    """Find the best match for a user among all available users."""
    # Generate summaries for all other users
    available_matches = []
    for name, data in eligible_users.items():
        chat_history = data.get('chat_history', [])
        
        # Extract key information from chat history
        interests = []
        skills = []
        goals = []
        project_ideas = []
        
        for msg in chat_history:
            content = msg.get('user', '').lower()
            bot_content = msg.get('bot', '').lower()
            
            # Extract interests
            if 'interested in' in content:
                interests.append(content.split('interested in')[1].strip())
            if 'project' in content and 'working on' in content:
                project_ideas.append(content.split('working on')[1].strip())
            
            # Extract skills
            skill_keywords = ['ai', 'machine learning', 'chatbot', 'python', 'javascript', 'react', 'node', 'backend', 'frontend']
            for skill in skill_keywords:
                if skill in content or skill in bot_content:
                    skills.append(skill.title())
            
            # Extract goals
            goal_keywords = ['team', 'collaborate', 'build', 'create', 'develop', 'learn', 'mentor']
            for goal in goal_keywords:
                if goal in content or goal in bot_content:
                    goals.append(goal.title())
        
        # Calculate match score based on various factors
        match_score = 0
        match_factors = []
        
        # Score based on shared interests
        if interests:
            match_score += 2
            match_factors.append(f"Shared interests in: {', '.join(interests[:2])}")
        
        # Score based on complementary skills
        if len(skills) >= 2:
            match_score += 2
            match_factors.append(f"Technical skills: {', '.join(skills[:3])}")
        
        # Score based on project alignment
        if project_ideas:
            match_score += 1
            match_factors.append(f"Project focus: {project_ideas[0]}")
        
        # Score based on goals
        if goals:
            match_score += 1
            match_factors.append(f"Goals: {', '.join(goals[:2])}")
        
        available_matches.append({
            'name': name,
            'score': match_score,
            'factors': match_factors,
            'interests': list(set(interests)),
            'skills': list(set(skills)),
            'goals': list(set(goals)),
            'project_ideas': list(set(project_ideas))
        })
    
    # Sort matches by score
    available_matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Return the best match with detailed explanation
    if available_matches:
        match = available_matches[0]
        
        # Build detailed explanation
        explanation = f"""## Match Found! 🤝

I've found a great potential match with **{match['name']}**!

### Why This Match Works
{chr(10).join([f"- {factor}" for factor in match['factors']])}

### Shared Interests & Skills
- **Technical Focus**: {', '.join(match['skills'][:3]) if match['skills'] else 'Various technical skills'}
- **Project Goals**: {', '.join(match['project_ideas'][:2]) if match['project_ideas'] else 'Building innovative solutions'}
- **Collaboration Style**: {', '.join(match['goals'][:2]) if match['goals'] else 'Team-oriented approach'}

### Potential Collaboration Areas
1. **Project Development**: Combine your expertise to build something amazing
2. **Skill Sharing**: Learn from each other's strengths
3. **Innovation**: Create unique solutions using your combined knowledge

### Next Steps
1. Reach out to {match['name']} to discuss your shared interests
2. Explore potential project ideas together
3. Start planning your collaboration!"""
        
        return {
            'match': match['name'],
            'explanation': explanation,
            'score': match['score']
        }
    else:
        return {
            'match': None,
            'explanation': "No suitable matches found at this time. Keep chatting to find potential matches!",
            'score': 0
        } 