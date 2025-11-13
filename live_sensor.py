import serial
import time
import sys
import paho.mqtt.client as mqtt  # <--- ADDED
import json                      # <--- ADDED

# --- CONFIGURATION ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200
# --- END CONFIGURATION ---

# <--- ADDED: MQTT Configuration ---
BROKER_ADDRESS = "localhost"
CLIENT_ID = "plant_sensor_publisher"
TOPIC_SENSOR_DATA = "plant/sensor/data"
TOPIC_SENSOR_REQUEST = "plant/sensor/request"
# --- END MQTT ---


def connect_to_esp32(port, baud):
    """
    Tries to connect to the serial port.
    Returns the serial object or None on failure.
    """
    try:
        print(f"Attempting to connect to {port} at {baud} baud...")
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)
        ser.flushInput()
        print(f"Successfully connected to {port} and cleared buffer.")
        return ser
    except serial.SerialException:
        print(f"--- CRITICAL ERROR ---")
        print(f"Could not open port {port}.")
        # (Your error messages are good)
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


def read_and_parse_data(ser):
    """
    Reads one line from serial, decodes it, and parses it.
    Returns a dictionary of data or None.
    """
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()

        if not line:
            # This is just a timeout, not an error.
            # print("...Waiting for data...")
            return None

        # This check is good. It ensures all keys are present.
        if "temp:" in line and "humidity:" in line and "soil_perc:" in line and "lux:" in line:
            
            sensor_data = {}
            parts = line.split(',')
            
            for part in parts:
                key_value = part.split(':')
                if len(key_value) == 2:
                    key = key_value[0].strip()
                    value_str = key_value[1].strip()
                    
                    try:
                        sensor_data[key] = float(value_str)
                    except ValueError:
                        print(f"(Warning) Could not parse value: {value_str}")
                        sensor_data[key] = None
            
            return sensor_data
        else:
            print(f"(ESP32 JUNK): Ignoring line: {line}")
            return None
            
    except Exception as e:
        print(f"An error occurred while reading: {e}")
        return None

# <--- ADDED: MQTT Connection Functions ---
def connect_mqtt(ser_object):
    """Connects to the MQTT broker."""
    
    def on_connect(client, userdata, flags, rc, properties=None):
        if rc == 0:
            print("Sensor script connected to MQTT Broker.")
            client.subscribe(TOPIC_SENSOR_REQUEST)
            print(f"Subscribed to {TOPIC_SENSOR_REQUEST}")
        else:
            print(f"Failed to connect to MQTT, return code {rc}")

    def on_message(client, userdata, msg):
        """Called when the 'Live Data' button is pressed in the UI."""
        print(f"Received manual update request on topic {msg.topic}")
        try:
            # We stored the serial object in 'userdata'
            # This writes the 'r' character (for 'read') to the ESP32
            userdata.write(b'r\n') 
            print("Sent 'r' command to ESP32 for immediate reading.")
        except Exception as e:
            print(f"Error writing to serial port: {e}")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
    client.on_connect = on_connect
    client.on_message = on_message
    
    # --- This is the key ---
    # We store the 'ser' object in the client's user_data,
    # so on_message can access it.
    client.user_data_set(ser_object) 
    
    try:
        client.connect(BROKER_ADDRESS)
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        return None
        
    return client
# --- END MQTT ---


# --- MAIN PROGRAM (MODIFIED) ---
if __name__ == "__main__":
    
    ser = connect_to_esp32(SERIAL_PORT, BAUD_RATE)
    
    if not ser:
        print("Could not connect to ESP32. Exiting.")
        sys.exit(1)
        
    # <--- ADDED: Connect to MQTT ---
    client = connect_mqtt(ser)
    
    if not client:
        print("Could not connect to MQTT. Exiting.")
        ser.close()
        sys.exit(1)

    # Start the MQTT client in a background thread
    # This will listen for 'on_message' requests
    client.loop_start() 

    print("\n--- Starting to read data (Press Ctrl+C to stop) ---")
    try:
        while True:
            # Read and parse one line of data (this will block until
            # the ESP32 sends a line or the 2-second timeout hits)
            data = read_and_parse_data(ser)
            
            # If data is not None, the parsing was successful
            if data:
                print(f"[{time.ctime()}] SUCCESS: {data}")
                
                # <--- ADDED: Publish data to MQTT ---
                payload = json.dumps(data)
                result = client.publish(TOPIC_SENSOR_DATA, payload)
                
                if result[0] != 0:
                    print("...Failed to publish to MQTT.")
                    
    except KeyboardInterrupt:
        print("\nStopping read loop...")
    finally:
        # <--- ADDED: Clean up MQTT ---
        client.loop_stop()
        client.disconnect()
        print("MQTT connection closed.")
        
        ser.close()
        print("Serial connection closed.")

    print("Exiting.")
