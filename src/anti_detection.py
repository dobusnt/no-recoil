import random
import time
import math
import threading
import os
import sys

class AntiDetectionSystem:
    def __init__(self):
        self.humanization_level = 3  # 1-5 scale
        self.process_obfuscation_active = False
        self.variable_timing_enabled = True
        self.enable_advanced_movement = True
        self.smart_activation = True
        
        # Humanization parameters
        self.timing_variation = 0.2  
        self.movement_variation = 0.15  
        self.micro_pause_chance = 0.05 
        
        # 
        self.activation_delay_min = 0.01
        self.activation_delay_max = 0.03
        self.skip_chance = 0.03  
        
        # Bezier curve control points for more natural movement
        self.bezier_points = 3
        
        # Start protection thread
        self._protection_active = True
        self._protection_thread = threading.Thread(target=self._protection_loop, daemon=True)
        self._protection_thread.start()
    
    def humanize_movement(self, x, y):
        """Apply human-like imperfections to mouse movements"""
        if not random.random() < self.skip_chance:
            # Apply small random variations to movement
            variation_x = random.uniform(-self.movement_variation, self.movement_variation)
            variation_y = random.uniform(-self.movement_variation, self.movement_variation)
            
            x_human = x * (1 + variation_x)
            y_human = y * (1 + variation_y)
            
            return x_human, y_human
        else:
            # Occasionally skip movement (human error simulation)
            return 0, 0
    
    def humanize_delay(self, delay):
        """Apply human-like variations to timing"""
        if self.variable_timing_enabled:
            # Base randomization
            humanized_delay = delay * random.uniform(1 - self.timing_variation, 1 + self.timing_variation)
            
            # Occasionally add a micro pauses
            if random.random() < self.micro_pause_chance:
                humanized_delay += random.uniform(0.005, 0.02)
                
            return max(0.001, humanized_delay)
        return delay
    
    def get_activation_delay(self):
        """Get a randomized activation delay"""
        if self.smart_activation:
            return random.uniform(self.activation_delay_min, self.activation_delay_max)
        return 0
    
    def calculate_bezier_path(self, start_x, start_y, end_x, end_y, num_points=10):
        """Calculate a bezier curve path between two points for natural movement"""
        if not self.enable_advanced_movement:
            return [(end_x, end_y)]
            
        # Create control points for bezier curve
        control_points = []
        control_points.append((start_x, start_y))
        
        for i in range(self.bezier_points - 2):
            t = (i + 1) / (self.bezier_points - 1)
            mid_x = start_x + (end_x - start_x) * t
            mid_y = start_y + (end_y - start_y) * t
            rand_x = mid_x + random.uniform(-abs(end_x - start_x) * 0.1, abs(end_x - start_x) * 0.1)
            rand_y = mid_y + random.uniform(-abs(end_y - start_y) * 0.1, abs(end_y - start_y) * 0.1)
            
            control_points.append((rand_x, rand_y))
            
        control_points.append((end_x, end_y))
        
        # Calculate points along the bezier curve
        path = []
        for t in [i / (num_points - 1) for i in range(num_points)]:
            x, y = self._bezier_point(control_points, t)
            path.append((x, y))
            
        return path[1:]  # Skip the first point (starting position)
    
    def _bezier_point(self, control_points, t):
        """Calculate a point on a bezier curve at parameter t"""
        n = len(control_points) - 1
        x = 0
        y = 0
        
        for i, point in enumerate(control_points):
            binom = math.comb(n, i)
            mult = binom * (t ** i) * ((1 - t) ** (n - i))
            x += mult * point[0]
            y += mult * point[1]
            
        return x, y
    
    def _protection_loop(self):
        """Background protection thread to help evade detection"""
        while self._protection_active:
            # Sleep to avoid high CPU usage
            time.sleep(5)
            
            if self.process_obfuscation_active:
                # Change process priority randomly (this kind of helps with detection)
                if random.random() < 0.3:
                    try:
                        if sys.platform == 'win32':
                            os.system(f"wmic process where processid={os.getpid()} CALL setpriority \"{'normal' if random.random() < 0.5 else 'below normal'}\"")
                    except:
                        pass
    
    def should_skip_compensation(self):
        """Decides if we should skip compensation for this shot (to seem more human)"""
        return random.random() < self.skip_chance
    
    def adaptive_timing(self, base_delay, consecutive_shots):
        """Adjust timing based on consecutive shots (humans slow down)"""
        fatigue_factor = min(consecutive_shots * 0.005, 0.1) 
        return base_delay * (1 + fatigue_factor)
    
    def cleanup(self):
        """Stop protection thread"""
        self._protection_active = False
        if self._protection_thread.is_alive():
            self._protection_thread.join(timeout=1.0) 
