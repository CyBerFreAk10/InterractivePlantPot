from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty, ObjectProperty
from kivy.animation import Animation
from kivy.clock import Clock
# --- MODIFIED: Changed Popup to ModalView to fix keyboard ---
from kivy.uix.modalview import ModalView
from kivy.uix.spinner import Spinner
import os
import json

# --- VOICE & MQTT IMPORTS ---
import paho.mqtt.client as mqtt

# --- NO AI OR SENSOR IMPORTS HERE ---

KV_STRING = """
<MainLayout>:
    Image:
        id: video_screen_a
        fit_mode: "cover"
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        opacity: 1
    Image:
        id: video_screen_b
        fit_mode: "cover"
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        opacity: 0
    Button:
        id: touch_button
        size_hint: 0.4, 0.6
        pos_hint: {'center_x': 0.5, 'center_y': 0.45}
        background_color: 0, 0, 0, 0 # Invisible
        on_press: root.play_touch_effect()

    Button:
        text: 'Exit'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'x': 0.02, 'top': 0.98}
        on_press: app.stop()
        background_color: 0.8, 0.2, 0.2, 0.9
    Button:
        text: 'Live Data'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'right': 0.98, 'top': 0.98}
        on_press: root.update_with_live_data()
        background_color: 0.2, 0.5, 0.8, 0.9
    Button:
        text: 'PlantAI'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'x': 0.02, 'y': 0.02}
        on_press: root.show_plant_ai()
        background_color: 0.2, 0.7, 0.3, 0.9
    Button:
        text: 'Plant Info'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'right': 0.98, 'y': 0.02}
        on_press: root.show_plant_info()
        background_color: 0.2, 0.7, 0.3, 0.9

# --- MODIFIED: Changed from Popup to ModalView ---
<PlantAiPopup>:
    id: ai_popup
    size_hint: 0.9, 0.7
    auto_dismiss: False
    
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: 0.1, 0.12, 0.15, 0.9
            Rectangle:
                pos: self.pos
                size: self.size
        
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Label:
                text: "Welcome to PlantAi"
                font_size: '20sp'
                halign: 'center'
                valign: 'middle'
            Button:
                text: "X"
                size_hint: None, None
                size: '40dp', '40dp'
                on_press: root.dismiss()
        
        ScrollView:
            size_hint: 1, 1
            scroll_y: 0 
            Label:
                id: chat_history
                text: "[color=AAAAAA]Chat history will appear here...[/color]\\n"
                markup: True
                font_size: '16sp'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                padding: '10dp', '10dp'
                
        BoxLayout:
            size_hint_y: None
            height: '50dp'
            spacing: '10dp'
            TextInput:
                id: text_input
                hint_text: "Ask your plant..."
                size_hint_x: 0.7
                use_vkeyboard: True
                multiline: False
                on_text_validate: root.send_chat_message(self)
            Button:
                id: send_button
                text: "Send"
                size_hint_x: 0.15
                on_press: root.send_chat_message(text_input)
            Button:
                id: mic_button
                text: "Mic"
                size_hint_x: 0.15
                on_press: root.mic_pressed()

# --- MODIFIED: Changed from Popup to ModalView ---
<PlantInfoPopup>:
    id: info_popup
    size_hint: 0.9, 0.7
    auto_dismiss: False
    
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: 0.1, 0.12, 0.15, 0.9
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Label:
                text: "Plant Information"
                font_size: '20sp'
                halign: 'center'
                valign: 'middle'
            Button:
                text: "X"
                size_hint: None, None
                size: '40dp', '40dp'
                on_press: root.dismiss()
        Spinner:
            id: plant_spinner
            text: 'Money Plant'
            values: ['Money Plant']
            size_hint: 1, None
            height: '44dp'
        ScrollView:
            size_hint: 1, 1
            do_scroll_x: False
            Label:
                size_hint_y: None
                height: self.texture_size[1]
                padding: '10dp', '10dp'
                text_size: self.width, None
                halign: 'left'
                valign: 'top'
                markup: True
                text:
                    "[b]Plant Type:[/b] Money Plant (Epipremnum aureum)\\n\\n" + \\
                    "[b]Sunlight:[/b]\\n" + \\
                    "Prefers bright, indirect light. Can tolerate low light, " + \\
                    "but growth may be slower. Avoid direct, harsh sunlight, " + \\
                    "which can scorch the leaves.\\n\\n" + \\
                    "[b]Watering:[/b]\\n" + \\
                    "Water thoroughly when the top 1-2 inches of soil feel dry. " + \\
                    "Allow soil to dry out between waterings. Overwatering is " + \\
                    "the most common mistake and leads to root rot.\\n\\n" + \\
                    "[b]Soil:[/b]\\n" + \\
                    "Use any well-draining potting mix.\\n\\n" + \\
                    "[b]Toxicity:[/b]\\n" + \\
                    "Mildly toxic to pets and humans if ingested. Keep out of reach."

# --- MODIFIED: Changed from Popup to ModalView ---
<LiveDataPopup>:
    id: data_popup
    size_hint: 0.9, 0.5
    auto_dismiss: False
    
    BoxLayout:
        orientation: 'vertical'
        padding: '10dp'
        spacing: '10dp'
        canvas.before:
            Color:
                rgba: 0.1, 0.12, 0.15, 0.9
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: '40dp'
            Label:
                text: "Live Sensor Data"
                font_size: '20sp'
                halign: 'center'
                valign: 'middle'
            Button:
                text: "X"
                size_hint: None, None
                size: '40dp', '40dp'
                on_press: root.dismiss()
        BoxLayout:
            orientation: 'vertical'
            padding: '10dp'
            spacing: '15dp'
            Label:
                id: temp_label
                text: "Temperature: -- °C"
                font_size: '18sp'
            Label:
                id: humidity_label
                text: "Humidity: -- %"
                font_size: '18sp'
            Label:
                id: light_label
                text: "Ambient Light: -- lux"
                font_size: '18sp'
            Label:
                id: moisture_label
                text: "Soil Moisture: -- %"
                font_size: '18sp'
""" 
Builder.load_string(KV_STRING)

# --- MQTT Settings ---
BROKER_ADDRESS = "localhost"
CLIENT_ID = "plant_ui"
TOPIC_UI_UPDATE = "plant/ui/update"
TOPIC_SENSOR_REQUEST = "plant/sensor/request"
TOPIC_CHAT_REQUEST = "plant/chat/request"


# --- MODIFIED: Changed from Popup to ModalView ---
class PlantAiPopup(ModalView):
    main_layout = ObjectProperty(None)
    
    def on_open(self):
        # --- MODIFIED: Schedule focus to fix keyboard ---
        # This waits 0.1s for the popup to finish opening, then forces focus
        Clock.schedule_once(self.set_focus_on_input, 0.1)
        
    def set_focus_on_input(self, dt):
        """Forces focus on the text input."""
        self.ids.text_input.focus = True
        
    def on_dismiss(self):
        """Called when the popup is closed."""
        if self.main_layout:
            self.main_layout.ai_popup = None
            # --- MODIFIED: Clear the focus flag ---
            self.main_layout.popup_is_open = False

    def send_chat_message(self, text_input_widget):
        message = text_input_widget.text
        if not message:
            print("No message to send.")
            return

        self.ids.chat_history.text += f"[color=3399FF]You:[/color] {message}\n"
        
        if self.main_layout and self.main_layout.mqtt_client:
            try:
                print(f"Sending chat message: '{message}'")
                self.main_layout.mqtt_client.publish(TOPIC_CHAT_REQUEST, message)
                text_input_widget.text = ""
                # --- MODIFIED: Re-focus after sending ---
                self.ids.text_input.focus = True
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to publish MQTT message: {e}")
                self.ids.chat_history.text += f"[color=FF0000]Error: Could not send message.[/color]\n"
        else:
            print("ERROR: Cannot send message. No main_layout or mqtt_client found.")

    def mic_pressed(self):
        print("Mic button pressed! (Voice input not implemented yet)")
        self.ids.chat_history.text += f"[color=AAAAAA]Voice input is not connected yet...[/color]\n"


# --- MODIFIED: Changed from Popup to ModalView ---
class PlantInfoPopup(ModalView):
    # --- MODIFIED: Added main_layout property and dismiss method ---
    main_layout = ObjectProperty(None)
    
    def on_dismiss(self):
        if self.main_layout:
            self.main_layout.popup_is_open = False

# --- MODIFIED: Changed from Popup to ModalView ---
class LiveDataPopup(ModalView):
    main_layout = ObjectProperty(None)
    
    def on_dismiss(self):
        print("Live Data popup closed.")
        if self.main_layout:
            self.main_layout.live_data_popup = None
            # --- MODIFIED: Clear the focus flag ---
            self.main_layout.popup_is_open = False

# --- MAIN LAYOUT CLASS ---
class MainLayout(FloatLayout):
    active_screen_id = StringProperty('a')
    current_image_path = StringProperty("")
    image_to_revert_to = StringProperty("")
    touch_revert_event = None
    mqtt_client = None
    live_data_popup = ObjectProperty(None, allownone=True)
    ai_popup = ObjectProperty(None, allownone=True)
    
    # --- MODIFIED: Added new flag for focus fix ---
    popup_is_open = BooleanProperty(False)

    base_image_path = os.path.expanduser("~/Documents/MiniProject/images")
    image_map = {
        "happy": os.path.join(base_image_path, "happy_plant.jpeg"),
        "thirsty": os.path.join(base_image_path, "plant_thirsty.jpeg"),
        "sad": os.path.join(base_image_path, "plant_in_dark.jpeg"),
        "overwatered": os.path.join(base_image_path, "plant_in_dark.jpeg"),
        "low_light": os.path.join(base_image_path, "plant_in_dark.jpeg"),
        "high_light": os.path.join(base_image_path, "plant_enjoying_sun.jpeg"),
        "smart": os.path.join(base_image_path, "happy_plant.jpeg"),
        "touched": os.path.join(base_image_path, "plant_touched.jpeg"),
        "neutral": os.path.join(base_image_path, "happy_plant.jpeg"),
    }
    
    def on_kv_post(self, base_widget):
        print("UI is ready. Starting with default image.")
        default_image = self.image_map.get('neutral', list(self.image_map.values())[0])
        self.ids.video_screen_a.source = default_image
        self.current_image_path = default_image
        self.setup_mqtt()

    def setup_mqtt(self):
        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                print("UI connected to MQTT Broker.")
                client.subscribe(TOPIC_UI_UPDATE)
                print(f"Subscribed to {TOPIC_UI_UPDATE}")
            else:
                print(f"Failed to connect, return code {rc}")

        def on_message(client, userdata, msg):
            print(f"Received UI update on {msg.topic}")
            try:
                data = json.loads(msg.payload.decode())
                Clock.schedule_once(lambda dt: self.update_ui_visuals(data))
            except json.JSONDecodeError:
                print(f"Error: Received non-JSON message: {msg.payload}")
            except Exception as e:
                print(f"Error processing message: {e}")

        self.mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=CLIENT_ID)
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message
        try:
            self.mqtt_client.connect(BROKER_ADDRESS)
            self.mqtt_client.loop_start()
        except Exception as e:
            print(f"MQTT Connection Error: {e}. Check if broker is running.")

    def update_with_live_data(self, *args):
        if self.live_data_popup:
            return
        print("--- 'Live Data' button pressed. Opening popup and sending request. ---")
        # --- MODIFIED: Set the focus flag ---
        self.popup_is_open = True
        popup = LiveDataPopup()
        popup.main_layout = self
        self.live_data_popup = popup
        popup.open()
        if self.mqtt_client and self.mqtt_client.is_connected():
            self.mqtt_client.publish(TOPIC_SENSOR_REQUEST, "update_now")
        else:
            print("MQTT not connected. Cannot request sensor data.")

    def update_ui_visuals(self, data):
        """Receives the full payload OR a partial payload."""
        
        mood = data.get("mood")
        speech_text = data.get("speech") # This is now just "chat_text"
        moisture = data.get("moisture")
        light = data.get("light")
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        # --- Update Chat (from chat agent) ---
        if speech_text:
            print(f"AI Chat Response: '{speech_text}'")
            # --- MODIFIED: Check if popup exists before updating ---
            if self.ai_popup:
                self.ai_popup.ids.chat_history.text += f"[color=00FF7F]PlantAI:[/color] {speech_text}\n"

        # --- Update Mood/Image (from mood agent) ---
        # --- MODIFIED: Added check for popup_is_open ---
        if mood and not self.popup_is_open:
            print(f"AI Decision: Mood='{mood}' (Not updating image, popup is open)")
        elif mood:
            print(f"AI Decision: Mood='{mood}'")
            new_image_source = self.image_map.get(mood, self.image_map["neutral"])
            print(f"Updating image to mood: {mood}")
            self._transition_to_image(new_image_source)

        # --- Update the Live Data Popup (if it's open) ---
        if self.live_data_popup:
            print("Live Data popup is open. Updating labels.")
            popup_ids = self.live_data_popup.ids
            if temperature is not None:
                popup_ids.temp_label.text = f"Temperature: {temperature:.1f} °C"
            if humidity is not None:
                popup_ids.humidity_label.text = f"Humidity: {humidity:.1f} %"
            if light is not None:
                popup_ids.light_label.text = f"Ambient Light: {int(light)} lux"
            if moisture is not None:
                popup_ids.moisture_label.text = f"Soil Moisture: {int(moisture)} %"
                
    def _transition_to_image(self, new_source):
        if self.current_image_path == new_source:
            return
        print(f"Transition requested to: {new_source}")
        if not os.path.exists(new_source):
            print(f"ERROR: Failed to find image file: {new_source}")
            new_source = self.image_map["neutral"]
            if not os.path.exists(new_source):
                print("ERROR: Could not find neutral image either. Aborting transition.")
                return
        self.current_image_path = new_source
        inactive_screen_id = 'b' if self.active_screen_id == 'a' else 'a'
        inactive_screen = getattr(self.ids, f'video_screen_{inactive_screen_id}')
        inactive_screen.source = new_source
        Clock.schedule_once(self.start_transition, 0.05)

    def start_transition(self, dt):
        active_screen = getattr(self.ids, f'video_screen_{self.active_screen_id}')
        inactive_screen_id = 'b' if self.active_screen_id == 'a' else 'a'
        inactive_screen = getattr(self.ids, f'video_screen_{inactive_screen_id}')
        anim = Animation(opacity=0, duration=0.7)
        anim.bind(on_complete=self.on_fade_out_complete)
        anim.start(active_screen)
        Animation(opacity=1, duration=0.7).start(inactive_screen)

    def on_fade_out_complete(self, animation, faded_out_widget):
        self.active_screen_id = 'b' if self.active_screen_id == 'a' else 'a'
        print(f"Fade complete. Active screen is now: video_screen_{self.active_screen_id}")

    def play_touch_effect(self):
        # --- MODIFIED: Check flag before playing effect ---
        if self.popup_is_open:
            print("Touch ignored, popup is open.")
            return
            
        if self.touch_revert_event:
            self.touch_revert_event.cancel()
            self.touch_revert_event = None
        if "touched" in self.image_map:
            print("Plant touched!")
            touched_image_source = self.image_map['touched']
            if self.current_image_path == touched_image_source:
                return
            self.image_to_revert_to = self.current_image_path
            self._transition_to_image(touched_image_source)
            self.touch_revert_event = Clock.schedule_once(self.on_touch_effect_finished, 2.0)
        else: 
            print("No 'touched' image defined.")

    def on_touch_effect_finished(self, dt):
        print("Touch effect finished. Reverting...")
        self.touch_revert_event = None
        revert_target = self.image_to_revert_to if self.image_to_revert_to else self.image_map['neutral']
        self._transition_to_image(revert_target)
        self.image_to_revert_to = ""

    def show_plant_ai(self):
        print("PlantAI button pressed.")
        if self.ai_popup:
            return
        # --- MODIFIED: Set the focus flag ---
        self.popup_is_open = True
        popup = PlantAiPopup()
        popup.main_layout = self 
        self.ai_popup = popup
        popup.open()
        
    def show_plant_info(self):
        print("Plant Info button pressed.")
        # --- MODIFIED: Set the focus flag ---
        self.popup_is_open = True
        popup = PlantInfoPopup()
        # --- MODIFIED: Pass main_layout to the info popup ---
        popup.main_layout = self
        popup.open()
        
class PlantApp(App):
    def build(self):
        self.main_layout = MainLayout()
        return self.main_layout

    def on_stop(self):
        print("Application is stopping. Cleaning up resources.")
        if self.main_layout.touch_revert_event:
            self.main_layout.touch_revert_event.cancel()
        
        if self.main_layout.mqtt_client:
            if self.main_layout.mqtt_client.is_connected():
                self.main_layout.mqtt_client.loop_stop()
                self.main_layout.mqtt_client.disconnect()
            else:
                self.main_layout.mqtt_client.loop_stop()

if __name__ == '__main__':
    Window.softinput_mode = 'pan'
    PlantApp().run()
