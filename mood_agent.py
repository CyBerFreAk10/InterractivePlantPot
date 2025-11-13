import paho.mqtt.client as mqtt
import json

# --- IMPORT THE AI FUNCTION FOR MOOD ---
try:
    # This assumes get_plant_status is in your ai_agent_test_code file
    from ai_agent_test_code import get_plant_status
    print("Successfully imported REAL get_plant_status function.")
except ImportError:
    print("WARNING: 'get_plant_status' not found. Using placeholder.")
    # Create a basic placeholder
    def get_plant_status(data):
        # A simple placeholder logic
        if data.get("soil_perc", 50) < 30:
            return "thirsty", "I'm so thirsty!"
        elif data.get("lux", 1000) < 500:
            return "sad", "It's too dark in here."
        else:
            return "happy", "I'm feeling great!"

# --- MQTT Settings ---
BROKER_ADDRESS = "localhost"
CLIENT_ID = "plant_mood_agent"
TOPIC_SENSOR_DATA = "plant/sensor/data"
TOPIC_UI_UPDATE = "plant/ui/update"

def connect_mqtt():
    """Connects to the MQTT broker."""
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Mood Agent connected to MQTT Broker.")
            # Subscribe to the raw sensor data
            client.subscribe(TOPIC_SENSOR_DATA)
            print(f"Subscribed to {TOPIC_SENSOR_DATA}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(client, userdata, msg):
        """Called when new sensor data is published from live_sensor.py"""
        
        print(f"Received sensor data on {msg.topic}")
        try:
            # 1. Get all sensor data
            sensor_data = json.loads(msg.payload.decode())
            print(f"Processing data: {sensor_data}")

            # 2. Run the AI "brain" to get mood and speech
            mood, speech_text = get_plant_status(sensor_data)
            
            # 3. Prepare the full payload for the UI
            # This payload includes EVERYTHING the UI needs:
            # - Mood/Speech for the main screen
            # - All 4 sensor values for the "Live Data" popup
            payload = {
                "mood": mood,
                "speech": speech_text,
                # Translate keys to match what UI expects
                "temperature": sensor_data.get("temp"), 
                "humidity": sensor_data.get("humidity"),
                "moisture": sensor_data.get("soil_perc"),
                "light": sensor_data.get("lux")
            }
            
            # 4. Publish the final, full payload to the UI
            client.publish(TOPIC_UI_UPDATE, json.dumps(payload))
            print(f"Published FULL UI update to {TOPIC_UI_UPDATE}")

        except json.JSONDecodeError:
            print(f"Error: Received non-JSON message: {msg.payload}")
        except Exception as e:
            print(f"Error processing sensor message: {e}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(BROKER_ADDRESS)
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        return None
        
    return client

def main():
    client = connect_mqtt()
    
    if not client:
        print("Exiting due to MQTT connection failure.")
        return

    print("Starting Mood Agent loop (listening for sensor data)...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nShutting down Mood Agent.")
        client.disconnect()

if __name__ == "__main__":
    main()
