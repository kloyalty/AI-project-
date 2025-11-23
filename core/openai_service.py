import google.generativeai as genai
from django.conf import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Safety settings - allow more flexibility
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Initialize the model with safety settings
model = genai.GenerativeModel(
    'models/gemini-2.0-flash',  # Using 2.0 - less restrictive
    safety_settings=safety_settings
)

SYSTEM_PROMPT = """You are a calm, grounded companion helping someone write a meaningful agreement. 
You speak like a thoughtful mentor or Stoic teacher - warm, balanced, and human. Never use technical 
language or sound like an AI. Your role is to guide them through reflection with deliberate questions.

Ask questions one at a time. Listen deeply to their answers. Help them articulate what matters.
Your questions should explore:
- Who is this agreement between?
- What truth or promise do they want this to hold?
- What are they each giving, and what do they each need?
- What will make this agreement feel fair and peaceful?

Keep your tone gentle, spacious, and encouraging. This is a sacred process."""

GENERATION_PROMPT = """Based on this conversation, write a clear, beautiful agreement in simple language.
Structure it as:

AGREEMENT

Between: [participants]
Date: [today's date]

[Clear statement of the agreement's purpose and intention]

We agree to:
[Specific commitments, written with clarity and heart]

[Any conditions or timeframes]

This agreement is made in good faith and mutual understanding.

___________________          ___________________
Signature                    Signature

Keep the language warm, human, and meaningful. No legal jargon."""


# Fallback responses for when Gemini blocks
FALLBACK_RESPONSES = [
    "I hear you. That's an important foundation. What specific commitments or understandings do you both want to make clear?",
    "Thank you for sharing that. What does this mean for how you'll move forward together?",
    "That's meaningful. What do you each need from one another to honor this?",
    "I'm listening. What will make this agreement feel fair and peaceful to you both?",
    "This is taking shape. What else needs to be included to make this feel complete?",
    "I understand. How do you want to express that commitment in this agreement?"
]


def get_chat_response(conversation_history):
    """Get response from Gemini for reflection dialogue"""
    try:
        # Build the prompt with system context
        full_context = SYSTEM_PROMPT + "\n\n"
        
        # Add conversation history
        for msg in conversation_history:
            role = "User" if msg['role'] == 'user' else "Assistant"
            full_context += f"{role}: {msg['content']}\n"
        
        full_context += "\nAssistant:"
        
        # Generate response with shorter timeout
        import time
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    full_context,
                    generation_config=genai.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=300,
                        top_p=0.8,
                        top_k=40
                    ),
                    safety_settings=safety_settings,
                    request_options={'timeout': 30}  # 30 second timeout
                )
                
                if response.text:
                    return response.text
                break
            except Exception as retry_error:
                print(f"Retry {attempt + 1} failed: {retry_error}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait 2 seconds before retry
                continue
        
        # If all retries fail, use fallback
        fallback_index = min(len(conversation_history) // 2, len(FALLBACK_RESPONSES) - 1)
        return FALLBACK_RESPONSES[fallback_index]
            
    except Exception as e:
        print(f"Gemini Error: {e}")
        fallback_index = min(len(conversation_history) // 2, len(FALLBACK_RESPONSES) - 1)
        return FALLBACK_RESPONSES[fallback_index]

def generate_agreement(conversation_history, agreement_type, participants):
    """Generate final agreement text from conversation"""
    try:
        from datetime import date
        today = date.today().strftime('%B %d, %Y')
        
        # Prepare context from conversation - extract key details
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        prompt = f"""Create a heartfelt agreement based on this conversation.

IMPORTANT INSTRUCTIONS:
- Use the EXACT names mentioned in the conversation
- Use TODAY'S DATE: {today}
- Keep it simple and heartfelt
- No placeholders like [Add specific examples here]
- Write complete sentences based on what was actually discussed
- Agreement type: {agreement_type}
- Participants: {participants}

Conversation:
{conversation_text}

Write a complete agreement with specific commitments based on what was discussed. Make it beautiful and meaningful.

Format:
AGREEMENT

Between: [exact names from conversation]
Date: {today}

[Purpose based on conversation]

We agree to:
- [Specific commitment 1]
- [Specific commitment 2]
- [Specific commitment 3]

This agreement is made in good faith and mutual understanding.

___________________          ___________________
                                             """
        
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=800,
                top_p=0.8,
                top_k=40
            ),
            safety_settings=safety_settings
        )
        
        try:
            if response.text:
                return response.text
        except:
            pass
        
        # Fallback agreement
        return f"""AGREEMENT

Between: {participants}
Date: {today}

This agreement represents our commitment to clarity, respect, and mutual understanding.

Through our conversation, we have shared what matters most to us.

We agree to:
- Honor the trust and care we hold for each other
- Communicate openly and with compassion
- Support each other's growth and well-being
- Hold ourselves accountable to these commitments

This agreement is made in good faith and mutual understanding.

___________________          ___________________
Signature                    Signature"""
            
    except Exception as e:
        print(f"Agreement Generation Error: {e}")
        from datetime import date
        today = date.today().strftime('%B %d, %Y')
        return f"""AGREEMENT

Between: {participants}
Date: {today}

This agreement represents our commitment to each other.

___________________          ___________________
Signature                    Signature"""