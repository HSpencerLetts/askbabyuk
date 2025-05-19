import os
from openai import OpenAI

# Initialise OpenAI client using secret from Replit env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_ellie_response(system_prompt: str, message_history: list) -> str:
    """
    Calls OpenAI API with system prompt and chat history.
    Returns Ellie's response text.
    """
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            *message_history
        ]
    )
    return response.choices[0].message.content.strip()
