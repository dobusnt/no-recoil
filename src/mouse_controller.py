import threading
import time
import random
import ctypes
import keyboard
from pynput import mouse
from pynput.mouse import Controller as MouseControl
import json
import os
from anti_detection import AntiDetectionSystem

# load windows user32.dll
user32 = ctypes.windll.user32

class MouseController:
    def __init__(self):
        self.running = False
        self.thread = None
        self.profile = None
        self.active_pattern = None
        self.current_step = 0
        self.mouse1_down = False
        self.mouse2_down = False
        self.is_active = False
        self.listener = None
        self.mouse = MouseControl()
        self.last_move_time = 0
        self.detection_avoidance = True
        self.move_methods = ["direct", "relative", "smooth"]
        self.current_move_method = "smooth"
        self.control_mode = "ads" 
        self.consecutive_shots = 0
        self.anti_detection = AntiDetectionSystem()
        
    def mouse_move(self, x, y):
        """Move the mouse by x, y with advanced anti-detection"""
        if self.detection_avoidance:
            # find where we are now
            curr_x, curr_y = self.mouse.position
            target_x, target_y = curr_x + x, curr_y + y
            
            # calculate fake human shift
            x_human, y_human = self.anti_detection.humanize_movement(x, y)
            humanized_target_x, humanized_target_y = curr_x + x_human, curr_y + y_human
            
            if self.current_move_method == "smooth" or self.current_move_method == "relative":
                # Use bezier curve for more natural movement
                path = self.anti_detection.calculate_bezier_path(
                    curr_x, curr_y, 
                    humanized_target_x, humanized_target_y, 
                    num_points=5 if self.current_move_method == "relative" else 8
                )
                
              
                for point_x, point_y in path:
                    # move to this point
                    self.mouse.position = (int(point_x), int(point_y))
                    tiny_delay = self.anti_detection.humanize_delay(0.001)
                    time.sleep(tiny_delay)
            else:
                self.mouse.move(int(x_human), int(y_human))
        else:
            self.mouse.move(int(x), int(y))
    
    def on_click(self, x, y, button, pressed):
        """handle clicks events, track left/right down"""
        if not self.profile:
            return
            
        button_str = str(button).lower()
        
        if 'left' in button_str:
            self.mouse1_down = pressed
            if pressed:
                self.current_step = 0  # reset pattern when you click
                
        if 'right' in button_str:
            self.mouse2_down = pressed
    
    def set_movement_method(self, method):
        """sets the movement method"""
        if method in self.move_methods:
            self.current_move_method = method
            return True
        return False
    
    def toggle_detection_avoidance(self):
        """toggle the detection avoidance features"""
        self.detection_avoidance = not self.detection_avoidance
        return self.detection_avoidance
    
    def set_control_mode(self, mode):
        """choose ads or non_ads"""
        if mode in ["ads", "non_ads"]:
            self.control_mode = mode
            return True
        return False
    
    def flip_active_state(self):
        """Toggle the active state"""
        self.is_active = not self.is_active
        self.consecutive_shots = 0  
        
        # add a small random delay after toggling
        time.sleep(random.uniform(0.05, 0.2))
    
    def toggle_compensation(self):
        """Toggle the recoil compensation on/off"""
        self.is_active = not self.is_active
        self.consecutive_shots = 0  
        
        # add a small random delay after toggling
        time.sleep(random.uniform(0.05, 0.2))
        
        status = "ON" if self.is_active else "OFF"
        print(f"Recoil compensation: {status}")
    
    def start_compensation(self, profile):
        """Start the recoil compensation with the given profile"""
        self.profile = profile
        
        require_toggle = profile.get('require_toggle', True)
        self.is_active = not require_toggle
        
        control_mode = profile.get('control_mode', 'ads')
        self.set_control_mode(control_mode)

        if 'movement_method' in profile:
            self.set_movement_method(profile.get('movement_method'))
            
        # get detection avoidance settings from the selected profile
        if 'detection_avoidance' in profile:
            self.detection_avoidance = profile.get('detection_avoidance', True)
        
        if self.running:
            return
            
        self.running = True

        self.thread = threading.Thread(target=self.compensation_thread)
        self.thread.daemon = True
        self.thread.start()
        
        # setups mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

        toggle_key = profile.get('toggle_key', 'f6')
        keyboard.add_hotkey(toggle_key, self.toggle_compensation)
        
        print(f"Recoil compensation started with profile: {profile.get('name', 'unknown')}")
        print(f"{'Toggle' if profile.get('require_toggle', True) else 'Always on'} mode: {toggle_key}")
        
        # show different instructions based on control mode
        if self.control_mode == "ads":
            print(f"Hold mouse1 (left) + mouse2 (right) to activate recoil control")
        else:
            print(f"Hold mouse1 (left) to activate recoil control")
            
        print(f"Using movement method: {self.current_move_method}")
        print(f"Detection avoidance: {'Enabled' if self.detection_avoidance else 'Disabled'}")
    
    def stop_compensation(self):
        """Stop the recoil compensation"""
        if not self.running:
            return
            
        self.running = False
        self.is_active = False

        if self.listener:
            self.listener.stop()
            self.listener = None

        keyboard.unhook_all_hotkeys()
        
        # wait for the thread to finish
        if self.thread:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        print("Recoil compensation stopped")
    
    def compensation_thread(self):
        """Thread for recoil compensation"""
        while self.running:
            try:
                if not self.profile:
                    time.sleep(0.1)
                    continue
                
                # check if recoil control should be active based on control mode
                is_active = False

                if self.control_mode == "ads" and self.mouse1_down and self.mouse2_down:
                    is_active = True
                elif self.control_mode == "non_ads" and self.mouse1_down:
                    is_active = True
                
                # apply recoil control if active and toggle is on
                if self.is_active and is_active:
                    if self.consecutive_shots == 0:
                        activation_delay = self.anti_detection.get_activation_delay()
                        time.sleep(activation_delay)
                    
                    # the program checks if we should skip this compensation (for a more human like behavior)
                    if self.detection_avoidance and self.anti_detection.should_skip_compensation():
                        time.sleep(self.profile.get('delay_rate', 7) * 0.01)
                        continue

                    pattern = self.profile.get('patterns', {}).get('default', [])
                    if not pattern:
                        time.sleep(0.05)
                        continue

                    index = min(self.consecutive_shots, len(pattern) - 1)
                    step = pattern[index]

                    try:
                        x = step["x"]
                        y = step["y"]
                        delay = step.get("delay", 0.01)
                    except (KeyError, TypeError):
                        # skips this step if values are missing or invalid
                        time.sleep(0.01)
                        continue
                    
                    # gets settings from profile
                    sensitivity = self.profile.get('sensitivity', 1.0)
                    strength = self.profile.get('recoil_strength', 1.0)
                    delay_rate = self.profile.get('delay_rate', 7) / 1000.0  

                    self.mouse_move(x, -y * strength * sensitivity)
                    
                    # Adaptive timing - delays increase slightly with consecutive shots
                    if self.detection_avoidance:
                        humanized_delay = self.anti_detection.adaptive_timing(delay_rate * 0.01, self.consecutive_shots)
                        time.sleep(self.anti_detection.humanize_delay(humanized_delay))
                    else:
                        # Regular delay
                        time.sleep(delay_rate * 0.01)
                    
                    # Increment consecutive shots counter
                    self.consecutive_shots += 1
                else:
                    # Reset consecutive shots when not firing
                    if self.consecutive_shots > 0:
                        self.consecutive_shots = 0
                        # Add a small recovery delay (like a human releasing trigger)
                        time.sleep(random.uniform(0.05, 0.15))
                    else:
                        # Standard sleep when not active
                        time.sleep(0.01)
            except Exception as e:
                print(f"Error in compensation thread: {e}")
                time.sleep(0.1) 
