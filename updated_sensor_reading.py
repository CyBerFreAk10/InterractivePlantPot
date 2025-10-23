'''
import random
import time

def read_simulated_sensors():
    """
    Generates a dictionary of fake sensor data with random values.
    This is used for testing the application without any physical hardware.

    Returns:
        A dictionary with simulated sensor data.
    """
    # Generate random values within a realistic range for each sensor
    data = {
        "soil": random.randint(10, 99),   # % moisture
        "light": random.randint(10, 99),  # % light level
        "temp": random.randint(15, 35)    # degrees Celsius
    }
    
    print(f"(SIMULATOR): Generated data: {data}")
    return data

# --- STANDALONE TEST BLOCK ---
# If you run this file directly (python sensor_simulator.py), it will generate data.
if __name__ == "__main__":
    print("\n--- Starting Standalone Simulator Test ---")
    print("Generating new simulated data every 100 seconds. Press Ctrl+C to stop.")
    while True:
        read_simulated_sensors()
        time.sleep(100)
        #Has been tested for every 5, 60 and 25 seconds and some extra values 
        '''
import serial
import json
import time

# --- CONFIGURATION ---
# This is the port your Arduino/ESP32 will be on.
# On Windows it might be 'COM3', on Linux '/dev/ttyUSB0' or '/dev/ttyACM0'
SERIAL_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 9600

# --- GLOBAL SERIAL OBJECT ---
# We try to initialize it once when the module is loaded.
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"Successfully connected to hardware on {SERIAL_PORT}")
    # Give the connection a moment to settle
    time.sleep(2) 
except serial.SerialException:
    print(f"CRITICAL ERROR: Could not connect to hardware on {SERIAL_PORT}.")
    print("The program can continue in simulated mode, but real data will not be available.")
    ser = None

def read_real_sensors():
    """
    Reads a line of data from the connected serial port, decodes it,
    and parses it as a JSON object.

    Returns:
        A dictionary with sensor data (e.g., {"soil": 55, "light": 60, "temp": 23})
        or None if an error occurs.
    """
    if not ser or not ser.is_open:
        # This check handles the case where the initial connection failed.
          print("Serial port is not available.") # Optional: uncomment for more verbose debugging
    return None

    try:
        # Read one line from the serial buffer, which should be a complete JSON string
        line = ser.readline().decode('utf-8').strip()

        # Check if we actually got any data
        if line:
            # Parse the JSON string into a Python dictionary
            sensor_data = json.loads(line)
            return sensor_data
        else:
            # The read timed out and we got nothing
            return None

    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"DATA ERROR: Could not decode or parse the data from the sensor: {e}")
        print(f"Received raw data: {line}")
        # Clear the buffer to prevent repeated errors on the same bad data
        ser.flushInput() 
        return None
    except Exception as e:
        print(f"UNEXPECTED SENSOR ERROR: An error occurred: {e}")
        return None

# --- STANDALONE TEST BLOCK ---
# If you run this file directly (python sensor_reader.py), it will test the connection.
if __name__ == "__main__":
    print("\n--- Starting Standalone Sensor Test ---")
    print("Attempting to read data every 5 seconds. Press Ctrl+C to stop.")
    while True:
        data = read_real_sensors()
        if data:
            print(f"[{time.ctime()}] SUCCESS: Read data: {data}")
        else:
            print(f"[{time.ctime()}] FAILED: No valid data received.")
        time.sleep(5)
