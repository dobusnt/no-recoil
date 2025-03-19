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

# Load the user32.dll for Windows
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
        self.control_mode = "ads"  # Default to ADS mode (both buttons)
        self.consecutive_shots = 0
        self.anti_detection = AntiDetectionSystem()
        
    def mouse_move(self, x, y):
        """Move the mouse by x, y with advanced anti-detection"""
        if self.detection_avoidance:
            # Get current position
            curr_x, curr_y = self.mouse.position
            target_x, target_y = curr_x + x, curr_y + y
            
            # Apply humanization to movement amounts
            x_human, y_human = self.anti_detection.humanize_movement(x, y)
            humanized_target_x, humanized_target_y = curr_x + x_human, curr_y + y_human
            
            if self.current_move_method == "smooth" or self.current_move_method == "relative":
                # Use bezier curve for more natural movement
                path = self.anti_detection.calculate_bezier_path(
                    curr_x, curr_y, 
                    humanized_target_x, humanized_target_y, 
                    num_points=5 if self.current_move_method == "relative" else 8
                )
                
                # Execute the path
                for point_x, point_y in path:
                    # Move to this point
                    self.mouse.position = (int(point_x), int(point_y))
                    # Small delay between points
                    tiny_delay = self.anti_detection.humanize_delay(0.001)
                    time.sleep(tiny_delay)
            else:
                # Direct method with humanization
                self.mouse.move(int(x_human), int(y_human))
        else:
            # Original direct movement
            self.mouse.move(int(x), int(y))
    
    def on_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.profile:
            return
            
        # Map button to string
        button_str = str(button).lower()
        
        # Track mouse1 (left click) state
        if 'left' in button_str:
            self.mouse1_down = pressed
            if pressed:
                self.current_step = 0  # Reset pattern on new click
                
        # Track mouse2 (right click) state
        if 'right' in button_str:
            self.mouse2_down = pressed
    
    def set_movement_method(self, method):
        """Set the movement method"""
        if method in self.move_methods:
            self.current_move_method = method
            return True
        return False
    
    def toggle_detection_avoidance(self):
        """Toggle detection avoidance features"""
        self.detection_avoidance = not self.detection_avoidance
        return self.detection_avoidance
    
    def set_control_mode(self, mode):
        """Set the control mode (ads or non_ads)"""
        if mode in ["ads", "non_ads"]:
            self.control_mode = mode
            return True
        return False
    
    def flip_active_state(self):
        """Toggle the active state"""
        self.is_active = not self.is_active
        self.consecutive_shots = 0  # Reset shot counter on toggle
        
        # Add a small random delay after toggling (to seem more natural)
        time.sleep(random.uniform(0.05, 0.2))
    
    def toggle_compensation(self):
        """Toggle the recoil compensation on/off"""
        self.is_active = not self.is_active
        self.consecutive_shots = 0  # Reset shot counter on toggle
        
        # Add a small random delay after toggling (to seem more natural)
        time.sleep(random.uniform(0.05, 0.2))
        
        status = "ON" if self.is_active else "OFF"
        print(f"Recoil compensation: {status}")
    
    def start_compensation(self, profile):
        """Start the recoil compensation with the given profile"""
        self.profile = profile
        
        # Get initial toggle state based on profile
        require_toggle = profile.get('require_toggle', True)
        self.is_active = not require_toggle
        
        # Get control mode from profile
        control_mode = profile.get('control_mode', 'ads')
        self.set_control_mode(control_mode)
        
        # Get movement method from profile if specified
        if 'movement_method' in profile:
            self.set_movement_method(profile.get('movement_method'))
            
        # Get detection avoidance setting from profile
        if 'detection_avoidance' in profile:
            self.detection_avoidance = profile.get('detection_avoidance', True)
        
        if self.running:
            # Already running, just update the profile
            return
            
        self.running = True
        
        # Start the compensation thread
        self.thread = threading.Thread(target=self.compensation_thread)
        self.thread.daemon = True
        self.thread.start()
        
        # Setup mouse listener
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        
        # Setup keyboard hotkey for toggling
        toggle_key = profile.get('toggle_key', 'f6')
        keyboard.add_hotkey(toggle_key, self.toggle_compensation)
        
        print(f"Recoil compensation started with profile: {profile.get('name', 'unknown')}")
        print(f"{'Toggle' if profile.get('require_toggle', True) else 'Always on'} mode: {toggle_key}")
        
        # Show different instructions based on control mode
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
        
        # Stop mouse listener
        if self.listener:
            self.listener.stop()
            self.listener = None
        
        # Remove all hotkeys
        keyboard.unhook_all_hotkeys()
        
        # Wait for thread to finish
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
                
                # Check if recoil control should be active based on control mode
                is_active = False
                
                # ADS mode requires both mouse buttons
                if self.control_mode == "ads" and self.mouse1_down and self.mouse2_down:
                    is_active = True
                # Non-ADS mode only requires left mouse button
                elif self.control_mode == "non_ads" and self.mouse1_down:
                    is_active = True
                
                # Apply recoil control if active and toggle is on
                if self.is_active and is_active:
                    # Smart activation - might add a small delay before starting compensation
                    if self.consecutive_shots == 0:
                        activation_delay = self.anti_detection.get_activation_delay()
                        time.sleep(activation_delay)
                    
                    # Check if we should skip this compensation (for more human behavior)
                    if self.detection_avoidance and self.anti_detection.should_skip_compensation():
                        time.sleep(self.profile.get('delay_rate', 7) * 0.01)
                        continue
                        
                    # Choose appropriate recoil pattern
                    pattern = self.profile.get('patterns', {}).get('default', [])
                    if not pattern:
                        time.sleep(0.05)
                        continue
                    
                    # Get the pattern step based on consecutive shots
                    index = min(self.consecutive_shots, len(pattern) - 1)
                    step = pattern[index]
                    
                    # Extract the values from the pattern step
                    try:
                        x = step["x"]
                        y = step["y"]
                        delay = step.get("delay", 0.01)
                    except (KeyError, TypeError):
                        # Skip this step if values are missing or invalid
                        time.sleep(0.01)
                        continue
                    
                    # Extract settings from profile
                    sensitivity = self.profile.get('sensitivity', 1.0)
                    strength = self.profile.get('recoil_strength', 1.0)
                    delay_rate = self.profile.get('delay_rate', 7) / 1000.0  # Convert ms to seconds
                    
                    # Simple recoil compensation (similar to Lua script)
                    # Move mouse down by recoil strength
                    # For recoil compensation, we need to counter upward recoil with downward movement
                    # Most mouse systems use negative Y for upward movement and positive Y for downward movement
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