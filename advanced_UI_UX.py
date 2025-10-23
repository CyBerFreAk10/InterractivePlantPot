from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty
from kivy.animation import Animation
from kivy.clock import Clock

# --- STEP 1: IMPORT YOUR "BRAIN" AND "NERVOUS SYSTEM" ---
try:
    # --- For testing WITHOUT hardware, use the simulator ---
    from sensor_simulator import read_simulated_sensors as read_real_sensors
    # --- To use your REAL hardware, comment out the line above and uncomment the line below ---
    # from sensor_reader import read_real_sensors

    from ai_agent_trimmed import get_plant_status, speak, cleanup
    
    print("Successfully imported AI agent and sensor modules.")

except ImportError as e:
    print(f"FATAL ERROR: Could not import modules. Make sure all files are in the same folder. Error: {e}")
    def get_plant_status(data): return "sad", "I can't find my brain!"
    def read_real_sensors(): return None
    def speak(text): print(f"DUMMY_TTS: {text}")
    def cleanup(): print("DUMMY_CLEANUP: Called.")

# Window.fullscreen = 'auto' # Keep this commented out for testing

KV_STRING = """
<MainLayout>:
    Video:
        id: video_player_a
        source: 'videos/Plant_Swaying_Video_Generation.mp4'
        state: 'play'
        options: {'loop': True}
        allow_stretch: True
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        opacity: 1
    Video:
        id: video_player_b
        state: 'stop'
        options: {'loop': True}
        allow_stretch: True
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        opacity: 0
    Button:
        size_hint: 0.4, 0.6
        pos_hint: {'center_x': 0.5, 'center_y': 0.45}
        background_color: 0, 0, 0, 0
        on_press: root.play_touch_video()
    BoxLayout:
        orientation: 'vertical'
        size_hint: 0.35, 0.4
        pos_hint: {'right': 0.98, 'center_y': 0.5}
        spacing: 15
        padding: 20
        canvas.before:
            Color:
                rgba: 0.1, 0.12, 0.15, 0.8
            RoundedRectangle:
                pos: self.pos
                size: self.size
                radius: [15]
        Label:
            id: moisture_label
            text: 'Soil Moisture: --%'
            font_size: '18sp'
            size_hint_y: None
            height: '30dp'
        Slider:
            id: moisture_slider
            min: 0
            max: 100
            value: 50
            disabled: True
            size_hint_y: None
            height: '48dp'
        Label:
            id: light_label
            text: 'Ambient Light: --%'
            font_size: '18sp'
            size_hint_y: None
            height: '30dp'
        Slider:
            id: light_slider
            min: 0
            max: 100
            value: 50
            disabled: True
            size_hint_y: None
            height: '48dp'
    Button:
        text: 'Exit'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'x': 0.02, 'top': 0.98}
        on_press: app.stop()
        background_color: 0.8, 0.2, 0.2, 0.9
    Button:
        text: 'Force Refresh'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'right': 0.98, 'top': 0.98}
        on_press: root.update_with_live_data()
        background_color: 0.2, 0.5, 0.8, 0.9
    Button:
        text: 'Camera'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'x': 0.02, 'y': 0.02}
        on_press: root.toggle_camera()
        background_color: (0.2, 0.8, 0.2, 0.9) if root.camera_active else (0.4, 0.4, 0.4, 0.9)
    Button:
        text: 'Mic'
        size_hint: None, None
        size: '150dp', '60dp'
        pos_hint: {'right': 0.98, 'y': 0.02}
        on_press: root.toggle_mic()
        background_color: (0.2, 0.8, 0.2, 0.9) if root.mic_active else (0.4, 0.4, 0.4, 0.9)
"""

Builder.load_string(KV_STRING)

class MainLayout(FloatLayout):
    camera_active = BooleanProperty(False)
    mic_active = BooleanProperty(False)
    active_player_id = StringProperty('a')
    previous_state = StringProperty('happy')

    video_map = {
        "happy": "videos/Plant_Swaying_Video_Generation.mp4",
        "thirsty": "videos/Thirsty_Plant_Video_Generation.mp4",
        # I commented the lines 137 and 138 because i didn't have the videos for it
        # Also use the correct path for the videos when executing
        #"sad": "videos/sad_placeholder.mp4", # You will need a generic sad video
        #"overwatered": "videos/overwatered_placeholder.mp4", # You need an overwatered video
        "low_light": "videos/Plant_Scared_of_the_Dark_Video.mp4",
        "high_light": "videos/Plant_Enjoys_Sun_In_Looping_Video.mp4",
        "smart": "videos/Plant_Acting_Smart_Video_Generation.mp4",
        "touched": "videos/Plant_Touched.mp4",
        "neutral": "videos/Plant_Swaying_Video_Generation.mp4"
    }

    def on_kv_post(self, base_widget):
        print("UI is ready. Starting the live data heartbeat.")
        Clock.schedule_interval(self.update_with_live_data, 15)
        self.update_with_live_data()

    def update_with_live_data(self, *args):
        print("\n--- Heartbeat Tick: Checking for new data... ---")
        sensor_data = read_real_sensors()
        if not sensor_data:
            print("Failed to get sensor data. Skipping update.")
            return

        mood, speech = get_plant_status(sensor_data)
        self.update_ui_visuals(mood, speech, sensor_data)
        
    def update_ui_visuals(self, mood, speech, sensor_data):
        print(f"AI Decision: Mood='{mood}', Speech='{speech}'")
        
        moisture = sensor_data.get("soil", 50)
        light = sensor_data.get("light", 50)
        self.ids.moisture_slider.value = moisture
        self.ids.light_slider.value = light
        self.ids.moisture_label.text = f"Soil Moisture: {int(moisture)}%"
        self.ids.light_label.text = f"Ambient Light: {int(light)}%"

        if mood in self.video_map:
            new_video_source = self.video_map[mood]
            self._transition_to_video(new_video_source, loop=True)
            speak(speech)
        else:
            print(f"ERROR: AI returned mood '{mood}' which has no video in video_map!")

    def _transition_to_video(self, new_source, loop=True):
        if self.active_player_id == 'a':
            active_player = self.ids.video_player_a
            inactive_player = self.ids.video_player_b
        else:
            active_player = self.ids.video_player_b
            inactive_player = self.ids.video_player_a
        
        if active_player.source == new_source:
            return

        inactive_player.source = new_source
        inactive_player.options['loop'] = loop
        inactive_player.state = 'play'
        if not loop:
            inactive_player.bind(on_eos=self.on_touch_video_finished)
        Clock.schedule_once(self.start_transition, 0.1)

    def start_transition(self, dt):
        if self.active_player_id == 'a':
            active_player = self.ids.video_player_a
            inactive_player = self.ids.video_player_b
        else:
            active_player = self.ids.video_player_b
            inactive_player = self.ids.video_player_a
        anim = Animation(opacity=0, duration=0.7)
        anim.bind(on_complete=self.on_fade_out_complete)
        anim.start(active_player)
        Animation(opacity=1, duration=0.7).start(inactive_player)
        
    def on_fade_out_complete(self, animation, faded_out_widget):
        faded_out_widget.state = 'stop'
        self.active_player_id = 'b' if self.active_player_id == 'a' else 'a'

    def play_touch_video(self):
        print("Plant touched!")
        touched_video_source = self.video_map['touched']
        self._transition_to_video(touched_video_source, loop=False)

    def on_touch_video_finished(self, video_player):
        print("Touch video finished. Reverting to previous state.")
        video_player.unbind(on_eos=self.on_touch_video_finished)
        self.update_with_live_data()

    def toggle_camera(self):
        self.camera_active = not self.camera_active
        print(f"Camera toggled: {'ON' if self.camera_active else 'OFF'}")

    def toggle_mic(self):
        self.mic_active = not self.mic_active
        print(f"Mic toggled: {'ON' if self.mic_active else 'OFF'}")

    def reset_sliders(self):
        print("This button is for manual override, which is disabled in live data mode.")

class PlantApp(App):
    def build(self):
        return MainLayout()

    def on_stop(self):
        print("Application is stopping. Cleaning up resources.")
        cleanup()

if __name__ == '__main__':
    PlantApp().run()

