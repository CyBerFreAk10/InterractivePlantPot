import paho.mqtt.client as mqtt
import json

# --- IMPORT YOUR REAL AI SCRIPT ---
try:
    # We ONLY need the chat function and cleanup
    from ai_agent_test_code import get_chat_response, cleanup
    print("Successfully imported REAL AI chat module.")
except ImportError:
    print("WARNING: 'get_chat_response' or 'cleanup' not found. Using placeholder.")
    # Create a basic placeholder
    def get_chat_response(text):
        text = text.lower()
        if "hello" in text:
            return "Hello there! How can I help?"
        elif "how are you" in text:
            return "I am feeling great, thanks for asking."
        else:
            return "I'm not sure how to answer that yet."
    def cleanup(): 
        pass

# --- MQTT Settings ---
BROKER_ADDRESS = "localhost"
CLIENT_ID = "plant_ai_agent"
TOPIC_UI_UPDATE = "plant/ui/update"
TOPIC_CHAT_REQUEST = "plant/chat/request" # <-- This is the only topic we listen to

def connect_mqtt():
    """Connects to the MQTT broker."""
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("AI Chat Agent connected to MQTT Broker.")
            # Subscribe ONLY to the chat topic
            client.subscribe(TOPIC_CHAT_REQUEST) 
            print(f"Subscribed to {TOPIC_CHAT_REQUEST}")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(client, userdata, msg):
        """Called ONLY when a chat message is published."""
        
        print(f"Received CHAT data on {msg.topic}")
        try:
            # 1. Get the chat message
            chat_message = msg.payload.decode()
            print(f"Processing chat: '{chat_message}'")
            
            # 2. Run the CHAT "brain"
            response_text = get_chat_response(chat_message)
            print(f"AI Chat Response: '{response_text}'")
            
            # 3. Prepare a SPEECH-ONLY payload
            ui_payload = {
                "speech": response_text
                # Note: We are not sending mood, moisture, or light
            }
            
            # 4. Publish the chat response
            client.publish(TOPIC_UI_UPDATE, json.dumps(ui_payload))
            print(f"Published SPEECH-ONLY update to {TOPIC_UI_UPDATE}")
            
        except Exception as e:
            print(f"Error processing chat message: {e}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS)
    return client

def main():
    client = connect_mqtt()
    print("Starting AI Chat Agent loop (listening for chat)...")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("Shutting down AI Agent.")
        cleanup() # Call your AI cleanup
        client.disconnect()

if __name__ == "__main__":
    main()
