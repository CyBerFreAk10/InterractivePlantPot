import ollama
import pyttsx3
import json
from datetime import datetime

# --- CONFIGURATION ---
# We are using a small, fast model. You can change this to a larger one if you have the resources.
OLLAMA_MODEL = 'gemma:2b' 

# --- ALARM THRESHOLDS ---
SOIL_CRITICALLY_LOW = 20
SOIL_CRITICALLY_HIGH = 95
TEMP_CRITICALLY_LOW = 15
TEMP_CRITICALLY_HIGH = 35
LIGHT_CRITICALLY_LOW = 20
LIGHT_CRITICALLY_HIGH = 95

# --- INITIALIZE TTS ENGINE ---
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"CRITICAL: Could not initialize TTS engine: {e}")
    engine = None

def speak(text):
    """Handles the text-to-speech functionality."""
    if engine and text:
        try:
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"Error during TTS speech: {e}")
    else:
        print(f"(Simulated Speech): {text}")

def agent_llm(sensor_data, emergency_context=None):
    """The core AI function that builds a prompt and calls the LLM."""
    soil = sensor_data.get("soil", 50)
    light = sensor_data.get("light", 50)
    temp = sensor_data.get("temp", 25)
    prompt = ""

    if emergency_context:
        # This map determines the REQUIRED mood for each emergency type.
        mood_map = {
            "thirsty": "thirsty", "happy": "happy", "neutral": "neutral",
            "scared": "low_light", "high_light": "high_light", "touched":"touched", "sad":"thirsty","hot":"high_light"
        }
        emergency_mood = mood_map.get(emergency_context, "sad")
        
        # --- THIS IS THE MODIFIED PROMPT ---
        prompt = f"""
        You are a plant. Your current critical status is '{emergency_context}'.
        Your task is to generate a short, creative, urgent sentence for this status.
        You must respond ONLY with a valid JSON object containing "mood" and "speech" keys.

        IMPORTANT: The value for the "mood" key in your JSON response MUST be exactly: "{emergency_mood}"

        Example response for a 'thirsty' status: {{"mood": "thirsty", "speech": "I'm so dry, I need water now!"}}
        
        Current status: '{emergency_context}'.
        Sensor data: Soil={soil}%, Light={light}%, Temp={temp}°C.
        """
    else:
        # This is the prompt for non-critical, ambient responses.
        now = datetime.now()
        current_time_str = now.strftime("%I:%M %p")
        # You can also add prompt engineering here if needed.
        allowed_moods = ["happy", "sad", "neutral"]
        prompt = f"""
        You are a cute plant pet. It is {current_time_str}.
        React to subtle, non-critical conditions. 
        Readings: Soil={soil}%, Light={light}%, Temp={temp}°C.
        Return your response as a single, valid JSON object with "mood" and "speech" keys.
        The "mood" value must be one of the following: {allowed_moods}.
        """
        
    try:
        # Send the prompt to the LLM
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}])
        text = response['message']['content']
        
        # Clean and parse the JSON response
        json_str = text[text.find('{'):text.rfind('}')+1]
        data = json.loads(json_str)
        
        mood = data.get("mood", "neutral")
        speech = data.get("speech", "")
        
        return mood, speech
        
    except Exception as e:
        print(f"Error processing LLM response: {e}. Defaulting to neutral.")
        return "neutral", "I'm feeling a bit quiet..."

def get_plant_status(sensor_data):
    """This is the main function called by the UI to check for alarms and get a response."""
    emergency_type = None
    soil_moisture = sensor_data.get("soil", 50)
    temperature = sensor_data.get("temp", 25)
    light_level = sensor_data.get("light", 50)
    
    # Check for critical conditions in a specific order of priority
    if soil_moisture < SOIL_CRITICALLY_LOW: emergency_type = "thirsty"
    elif soil_moisture > SOIL_CRITICALLY_HIGH: emergency_type = "overwatered"
    elif temperature < TEMP_CRITICALLY_LOW: emergency_type = "cold"
    elif temperature > TEMP_CRITICALLY_HIGH: emergency_type = "hot"
    elif light_level < LIGHT_CRITICALLY_LOW: emergency_type = "low_light"
    elif light_level > LIGHT_CRITICALLY_HIGH: emergency_type = "high_light"

    if emergency_type:
        print(f"Critical condition: {emergency_type}. Asking AI for creative response.")
        return agent_llm(sensor_data, emergency_context=emergency_type)
    else:
        # No critical issues, get an ambient response
        return agent_llm(sensor_data)

def cleanup():
    """A function to handle cleanup when the app closes."""
    print("AI Agent is shutting down.")

# Example of how to run this file for testing:
if __name__ == '__main__':
    print("--- Testing AI Agent Logic ---")
    
    # Test Case 1: Critical condition (thirsty)
    print("\n[Test Case 1: Thirsty]")
    test_data_thirsty = {"soil": 15, "light": 60, "temp": 22}
    mood, speech = get_plant_status(test_data_thirsty)
    print(f"  -> Mood: {mood}, Speech: '{speech}'")
    speak(speech)
    
    # Test Case 2: Non-critical (normal conditions)
    print("\n[Test Case 2: Normal]")
    test_data_normal = {"soil": 55, "light": 70, "temp": 24}
    mood, speech = get_plant_status(test_data_normal)
    print(f"  -> Mood: {mood}, Speech: '{speech}'")
    
    cleanup()