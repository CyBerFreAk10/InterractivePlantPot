PlantMate: Interactive Smart Plant Pot 🌱🤖

Overview

PlantMate is an IoT-powered smart plant pot designed to seamlessly connect environmental monitoring with an interactive user interface and local AI. This project bridges the gap between hardware sensors, microcontrollers, and intelligent backend processing to create a responsive, conversational planter that tells you exactly what it needs.

Key Features

Environmental Monitoring: Real-time sensor data collection (soil moisture, temperature, humidity, and light) handled by an ESP32.

Interactive Audio: Integrated microphone and speaker modules for two-way voice interaction and feedback.

Local AI Processing: Utilizes Ollama on the backend for intelligent, local processing of user voice inputs and sensor data.

Interactive GUI: A responsive dashboard hosted on a Raspberry Pi to visualize the plant's environment and mood.

Custom 3D Enclosure: A purpose-built, 3D-printed hardware housing designed in Autodesk Fusion 360.

Hardware Stack

Central Processor & Microcontroller: Raspberry Pi 5 (8GB), ESP32

Sensors: Capacitive Soil Moisture Sensor v2.0, DHT11 Temperature & Humidity Sensor, OPT3001 Light Sensor

Peripherals: 7" Touchscreen Display, USB Microphone, Mini Speaker

Enclosure: Custom 3D modeled chassis designed in Autodesk Fusion 360

Software Stack

Microcontroller Logic: C/C++ (ESP32 sensor integration and data transmission)

Application & GUI: Python 3.11+, Kivy 2.3+ (Raspberry Pi dashboard)

Networking & Communication: MQTT (paho-mqtt), PySerial

AI Backend & Audio: Ollama (gemma 2b), faster_whisper (Speech-to-Text), gTTS (Google Text-to-Speech)

The Team & Division of Labor

This collaborative project was built by splitting the development into dedicated hardware and software teams at Dr. AIT:

Hardware Architecture & 3D Design: Kishan H & Dhanush B R
(Custom 3D modeling, core electronics, ESP32 programming, sensor wiring, and mic/speaker configuration)

Pi Integration, MQTT & GUI: Edward C Daison
(Raspberry Pi setup, Kivy UI development, and MQTT broker network integration)

Backend & Conversational AI: M R Suhas
(Backend architecture, Gemma 2b AI model integration, and STT/TTS audio pipelines)
