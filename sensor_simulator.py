import random
import time

def read_simulated_sensors():
    """
    Generates a dictionary with random sensor data to simulate hardware.
    This allows the main application to run and be tested without a real device.
    """
    data = {
        "soil": random.randint(10, 99), 
        "light": random.randint(10, 99),
        "temp": random.randint(10, 40)
    }
    print(f"(SIMULATOR): Generated data: {data}")
    return data

# --- STANDALONE TEST BLOCK ---
# If you run this file directly (python sensor_simulator.py), it will generate data.
if __name__ == "__main__":
    print("\n--- Starting Standalone Simulator Test ---")
    print("Generating new simulated data every 5 seconds. Press Ctrl+C to stop.")
    while True:
        read_simulated_sensors()
        time.sleep(5)