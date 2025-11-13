# This is your new file: ai_agent_test_code.py

import ollama

# --- THIS IS THE CHAT FUNCTION YOUR AI AGENT IS LOOKING FOR ---
def get_chat_response(text):
    """
    Takes the user's text, sends it to Ollama, and returns the response.
    """
    print(f"\n(Gemma-2B): Received prompt: '{text}'")
    
    try:
        # Send the prompt to the Gemma-2B model
        # Make sure you have pulled this model! (ollama pull gemma:2b)
        response = ollama.chat(model='gemma:2b', messages=[
            {
                'role': 'user',
                'content': text,
            },
        ])
        
        # Extract the text content from the response
        reply = response['message']['content']
        
        print(f"(Gemma-2B): Generated response: '{reply}'")
        return reply

    except Exception as e:
        print(f"(Gemma-2B): CRITICAL ERROR: {e}")
        return "I'm having trouble connecting to my AI brain (Ollama)."

# --- THIS IS THE CLEANUP FUNCTION IT'S LOOKING FOR ---
def cleanup():
    """
    Called when the AI agent is shutting down.
    """
    print("(Gemma-2B): Cleanup called. Nothing to do.")
    pass

# --- THIS IS THE MOOD FUNCTION YOUR MOOD_AGENT.PY SCRIPT NEEDS ---
def get_plant_status(data):
    """
    This is the placeholder for your *mood* agent.
    It now uses the CORRECT keys from your sensor script.
    """
    print(f"(Mood Agent): Processing sensor data: {data}")
    
    # <--- THIS IS THE FIX ---
    # We are now using 'soil_perc' and 'lux', which match your sensor script.
    soil = data.get("soil_perc", 50)
    light = data.get("lux", 1000)
    temp = data.get("temp", 25)
    # --- END OF FIX ---

    # Now the logic will work correctly
    if soil < 30:
        return "thirsty", "I'm so thirsty! My soil is very dry."
    elif light < 500:
        return "sad", "It's so dark in here. I need more light."
    elif temp > 30:
        return "sad", "Phew, it is getting hot."
    else:
        return "happy", "I'm feeling great! My light and water are perfect."
