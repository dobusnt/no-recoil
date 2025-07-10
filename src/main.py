import os
import json
import time
import sys
import colorama
from colorama import Fore, Back, Style
from mouse_controller import MouseController
from config_manager import ConfigManager

# Initialize colorama for colored console output
colorama.init()

class NoRecoilApp:
    def __init__(self):
        # Display startup banner
        self.show_banner()
        
        print(f"{Fore.CYAN}Initializing application...{Style.RESET_ALL}")
        self.config_manager = ConfigManager()
        self.mouse_controller = MouseController()
        self.active = False
        self.current_profile = None
        self.profiles = {}
        self.load_profiles()
        
    def show_banner(self):
        banner = f"""
{Fore.RED}     ▄▄▄██▀▀▀██╗   ██╗██╗ ██████╗███████╗██████╗  █████╗ ███╗   ██╗████████╗
{Fore.RED}       ▒██  ██║   ██║██║██╔════╝██╔════╝██╔══██╗██╔══██╗████╗  ██║╚══██╔══╝
{Fore.RED}       ░██  ██║   ██║██║██║     █████╗  ██████╔╝███████║██╔██╗ ██║   ██║   
{Fore.RED}    ▓██▄██▓ ██║   ██║██║██║     ██╔══╝  ██╔══██╗██╔══██║██║╚██╗██║   ██║   
{Fore.RED}     ▓███▒  ╚██████╔╝██║╚██████╗███████╗██║  ██║██║  ██║██║ ╚████║   ██║   
{Fore.RED}     ▒▓▒▒░   ╚═════╝ ╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
{Fore.YELLOW}╔═════════════════════════════════════════════════════════════════════════╗
{Fore.YELLOW}║{Fore.RED} ☠️  CROSS-COMPATIBLE MOUSE MOVEMENT AUGMENTATION SYSTEM ☠️  {Fore.YELLOW}║
{Fore.YELLOW}╚═════════════════════════════════════════════════════════════════════════╝
{Fore.GREEN}v1.0 - _akk.{Style.RESET_ALL}
    {Fore.RED}[DANGER]{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}USE AT YOUR OWN RISK. FOR EDUCATIONAL PURPOSES ONLY.{Style.RESET_ALL}
"""
        print(banner)
        
    def load_profiles(self):
        """Load all profiles from the profiles directory"""
        print(f"{Fore.CYAN}Loading profiles...{Style.RESET_ALL}")
        profiles_dir = os.path.join(os.path.dirname(__file__), 'profiles')
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)
            
        profile_count = 0
        for filename in os.listdir(profiles_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(profiles_dir, filename), 'r') as f:
                        profile_data = json.load(f)
                        profile_name = os.path.splitext(filename)[0]
                        # Add name to profile data for reference
                        profile_data['name'] = profile_name
                        self.profiles[profile_name] = profile_data
                        print(f"{Fore.GREEN}Loaded profile: {profile_name}{Style.RESET_ALL}")
                        profile_count += 1
                except Exception as e:
                    print(f"{Fore.RED}Error loading profile {filename}: {e}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}Loaded {profile_count} profile(s){Style.RESET_ALL}")
        
        # Load the last used profile
        last_profile = self.config_manager.get_setting('last_profile')
        if last_profile and last_profile in self.profiles:
            self.select_profile(last_profile)
            print(f"{Fore.CYAN}Restored last profile: {last_profile}{Style.RESET_ALL}")
    
    def save_profile(self, name, data):
        """Save a profile to the profiles directory"""
        profiles_dir = os.path.join(os.path.dirname(__file__), 'profiles')
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)
            
        # Store name in profile data
        data['name'] = name
            
        filepath = os.path.join(profiles_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        self.profiles[name] = data
        print(f"{Fore.GREEN}Profile '{name}' saved successfully{Style.RESET_ALL}")
    
    def activate(self):
        """Activate no-recoil functionality"""
        if not self.current_profile:
            print(f"{Fore.RED}No profile selected. Please select a profile first.{Style.RESET_ALL}")
            return
            
        self.active = True
        print(f"{Fore.GREEN}Recoil control activated with profile: {self.current_profile}{Style.RESET_ALL}")
        
        try:
            # Start the recoil compensation in a separate thread (for optimization purposes)
            self.mouse_controller.start_compensation(self.profiles[self.current_profile])
        except KeyboardInterrupt:
            self.deactivate()
        except Exception as e:
            print(f"{Fore.RED}Error activating recoil compensation: {e}{Style.RESET_ALL}")
            self.active = False
    
    def deactivate(self):
        """Deactivate no-recoil functionality"""
        self.active = False
        self.mouse_controller.stop_compensation()
        print(f"{Fore.YELLOW}Recoil control deactivated{Style.RESET_ALL}")
    
    def select_profile(self, name):
        """Select a profile to use"""
        if name in self.profiles:
            self.current_profile = name
            # Save as last used profile
            self.config_manager.set_setting('last_profile', name)
            print(f"{Fore.GREEN}Profile '{name}' selected{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}Profile '{name}' not found{Style.RESET_ALL}")
            return False
    
    def set_movement_method(self):
        """Set the movement method"""
        print(f"\n{Fore.CYAN}=== Select Movement Method ==={Style.RESET_ALL}")
        print("1. Direct    - Fast single movement (may be detectable)")
        print("2. Relative  - Multi-step movements (better concealment)")
        print("3. Smooth    - Human-like movement curve (best concealment)")
        
        choice = input(f"\n{Fore.YELLOW}Enter choice (1-3): {Style.RESET_ALL}")
        method_map = {
            "1": "direct",
            "2": "relative", 
            "3": "smooth"
        }
        
        if choice in method_map:
            method = method_map[choice]
            if self.mouse_controller.set_movement_method(method):
                print(f"{Fore.GREEN}Movement method set to: {method}{Style.RESET_ALL}")
                
                # Save to current profile if one is selected
                if self.current_profile:
                    self.profiles[self.current_profile]['movement_method'] = method
                    self.save_profile(self.current_profile, self.profiles[self.current_profile])
            else:
                print(f"{Fore.RED}Invalid movement method{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Invalid choice{Style.RESET_ALL}")
    
    def toggle_detection_avoidance(self):
        """Toggle detection avoidance features"""
        status = self.mouse_controller.toggle_detection_avoidance()
        state = "Enabled" if status else "Disabled"
        print(f"{Fore.GREEN}Detection avoidance: {state}{Style.RESET_ALL}")
        
        # Save to current profile if one is selected
        if self.current_profile:
            self.profiles[self.current_profile]['detection_avoidance'] = status
            self.save_profile(self.current_profile, self.profiles[self.current_profile])
    
    def create_profile(self):
        """Create a new profile interactively"""
        name = input(f"{Fore.CYAN}Enter profile name: {Style.RESET_ALL}")
        if not name:
            print(f"{Fore.RED}Profile name cannot be empty{Style.RESET_ALL}")
            return
            
        if name in self.profiles:
            overwrite = input(f"{Fore.YELLOW}Profile '{name}' already exists. Overwrite? (y/n): {Style.RESET_ALL}")
            if overwrite.lower() != 'y':
                return
        
        print(f"{Fore.GREEN}Creating new profile...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Enter the following settings:{Style.RESET_ALL}")
        
        try:
            # Get basic settings
            sensitivity = float(input(f"{Fore.CYAN}Mouse sensitivity (default 1.0): {Style.RESET_ALL}") or "1.0")
            
            # Game type selection for control mode
            print(f"\n{Fore.CYAN}Select Game Type:{Style.RESET_ALL}")
            print("1. ADS-based games (Apex, Rainbow Six) - requires both mouse buttons")
            print("2. Non-ADS games (CS:GO, Valorant) - only requires left mouse button")
            
            game_choice = input(f"\n{Fore.YELLOW}Enter choice (1-2, default: 1): {Style.RESET_ALL}") or "1"
            control_mode = "ads" if game_choice == "1" else "non_ads"
            
            # Recoil preset selection
            print(f"\n{Fore.CYAN}Select Recoil Preset:{Style.RESET_ALL}")
            print("1. Low      - Minimal recoil compensation")
            print("2. Medium   - Moderate recoil compensation")
            print("3. High     - Strong recoil compensation")
            print("4. Ultra    - Very strong recoil compensation")
            print("5. Insanity - Extreme recoil compensation")
            print("6. Custom   - Custom recoil strength")
            
            preset_choice = input(f"\n{Fore.YELLOW}Enter choice (1-6, default: 2): {Style.RESET_ALL}") or "2"
            preset_map = {
                "1": "Low",
                "2": "Medium", 
                "3": "High",
                "4": "Ultra",
                "5": "Insanity",
                "6": "Custom"
            }
            recoil_preset = preset_map.get(preset_choice, "Medium")
            
            # Custom recoil strength if selected
            recoil_strength = 1.0
            if recoil_preset == "Custom":
                recoil_strength = int(input(f"{Fore.CYAN}Custom recoil strength (1-50, default 7): {Style.RESET_ALL}") or "7")
            
            # Toggle requirement
            print(f"\n{Fore.CYAN}Require toggle key to activate?{Style.RESET_ALL}")
            toggle_choice = input(f"{Fore.YELLOW}Require toggle? (y/n, default: y): {Style.RESET_ALL}") or "y"
            require_toggle = toggle_choice.lower() == "y"
            
            # Toggle key
            toggle_key_options = ["capslock", "numlock", "scrolllock", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
            print(f"\n{Fore.CYAN}Select toggle key: {', '.join(toggle_key_options)}{Style.RESET_ALL}")
            toggle_key = input(f"{Fore.YELLOW}Toggle key (default 'capslock'): {Style.RESET_ALL}").lower() or "capslock"
            
            # Delay rate
            delay_rate = int(input(f"{Fore.CYAN}Delay rate in ms (1-50, default 7): {Style.RESET_ALL}") or "7")
            
            # Movement method
            print(f"\n{Fore.CYAN}Select Movement Method:{Style.RESET_ALL}")
            print("1. Direct    - Fast single movement (may be detectable)")
            print("2. Relative  - Multi-step movements (better concealment)")
            print("3. Smooth    - Human-like movement curve (best concealment)")
            
            method_choice = input(f"\n{Fore.YELLOW}Enter choice (1-3, default: 3): {Style.RESET_ALL}") or "3"
            method_map = {
                "1": "direct", 
                "2": "relative", 
                "3": "smooth"
            }
            movement_method = method_map.get(method_choice, "smooth")
            
            # Detection avoidance (this is just for show, it doesn't actually do anything to avoid detection)
            print(f"\n{Fore.CYAN}Enable detection avoidance? (randomized movements){Style.RESET_ALL}")
            detection_choice = input(f"{Fore.YELLOW}Enable? (y/n, default: y): {Style.RESET_ALL}") or "y"
            detection_avoidance = detection_choice.lower() == "y"
            
            # Create a new profile with the provided settings
            profile_data = {
                "sensitivity": sensitivity,
                "control_mode": control_mode,
                "recoil_preset": recoil_preset,
                "recoil_strength": recoil_strength,
                "require_toggle": require_toggle,
                "toggle_key": toggle_key,
                "delay_rate": delay_rate,
                "movement_method": movement_method,
                "detection_avoidance": detection_avoidance,
                "patterns": {
                    "default": [
                        {"x": 0, "y": -5, "delay": 0.01},
                        {"x": 0, "y": -4, "delay": 0.01},
                        {"x": 1, "y": -4, "delay": 0.01},
                        {"x": 1, "y": -3, "delay": 0.01},
                        {"x": 0, "y": -3, "delay": 0.01},
                        {"x": -1, "y": -3, "delay": 0.01},
                        {"x": -1, "y": -2, "delay": 0.01},
                        {"x": 0, "y": -2, "delay": 0.01}
                    ]
                }
            }
            
            self.save_profile(name, profile_data)
            self.select_profile(name)
            
            print(f"{Fore.GREEN}Profile created successfully!{Style.RESET_ALL}")
            
        except ValueError as e:
            print(f"{Fore.RED}Invalid input: {e}{Style.RESET_ALL}")
    
    def edit_profile(self):
        """Edit an existing profile"""
        if not self.profiles:
            print(f"{Fore.RED}No profiles available. Create a profile first.{Style.RESET_ALL}")
            return
            
        print(f"\n{Fore.CYAN}Available profiles:{Style.RESET_ALL}")
        for name in self.profiles:
            marker = "*" if name == self.current_profile else " "
            print(f" {marker} {name}")
            
        name = input(f"\n{Fore.YELLOW}Enter profile name to edit: {Style.RESET_ALL}")
        if name not in self.profiles:
            print(f"{Fore.RED}Profile '{name}' not found{Style.RESET_ALL}")
            return
            
        profile = self.profiles[name]
        print(f"{Fore.GREEN}Editing profile '{name}'...{Style.RESET_ALL}")
        
        try:
            # Basic settings
            sensitivity = float(input(f"{Fore.CYAN}Mouse sensitivity (current: {profile.get('sensitivity', 1.0)}): {Style.RESET_ALL}") or profile.get('sensitivity', 1.0))
            
            # Game type/Control mode
            current_mode = profile.get('control_mode', 'ads')
            game_type_text = "ADS-based (Apex, R6)" if current_mode == "ads" else "Non-ADS (CS:GO, Valorant)"
            print(f"\n{Fore.CYAN}Select Game Type (current: {game_type_text}):{Style.RESET_ALL}")
            print("1. ADS-based games (Apex, Rainbow Six) - requires both mouse buttons")
            print("2. Non-ADS games (CS:GO, Valorant) - only requires left mouse button")
            
            mode_choice = input(f"\n{Fore.YELLOW}Enter choice (1-2, default: {1 if current_mode == 'ads' else 2}): {Style.RESET_ALL}") or ("1" if current_mode == "ads" else "2")
            control_mode = "ads" if mode_choice == "1" else "non_ads"
            
            # Recoil preset
            current_preset = profile.get('recoil_preset', 'Medium')
            print(f"\n{Fore.CYAN}Select Recoil Preset (current: {current_preset}):{Style.RESET_ALL}")
            print("1. Low      - Minimal recoil compensation")
            print("2. Medium   - Moderate recoil compensation")
            print("3. High     - Strong recoil compensation")
            print("4. Ultra    - Very strong recoil compensation")
            print("5. Insanity - Extreme recoil compensation")
            print("6. Custom   - Custom recoil strength")
            
            preset_map = {
                "1": "Low",
                "2": "Medium", 
                "3": "High",
                "4": "Ultra",
                "5": "Insanity",
                "6": "Custom",
                "Low": "1",
                "Medium": "2",
                "High": "3",
                "Ultra": "4",
                "Insanity": "5",
                "Custom": "6"
            }
            
            preset_choice = input(f"\n{Fore.YELLOW}Enter choice (1-6, default: {preset_map.get(current_preset, '2')}): {Style.RESET_ALL}") or preset_map.get(current_preset, "2")
            recoil_preset = preset_map.get(preset_choice, current_preset)
            
            # Custom recoil strength if selected
            recoil_strength = profile.get('recoil_strength', 1.0)
            if recoil_preset == "Custom":
                recoil_strength = int(input(f"{Fore.CYAN}Custom recoil strength (1-50, current: {recoil_strength}): {Style.RESET_ALL}") or recoil_strength)
            
            # Toggle requirement
            current_toggle_req = profile.get('require_toggle', True)
            toggle_default = "y" if current_toggle_req else "n"
            print(f"\n{Fore.CYAN}Require toggle key to activate?{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Current setting: {'Required' if current_toggle_req else 'Not required'}{Style.RESET_ALL}")
            toggle_choice = input(f"{Fore.YELLOW}Require toggle? (y/n, default: {toggle_default}): {Style.RESET_ALL}") or toggle_default
            require_toggle = toggle_choice.lower() == "y"
            
            # Toggle key
            current_toggle_key = profile.get('toggle_key', 'capslock')
            toggle_key_options = ["capslock", "numlock", "scrolllock", "f6", "f7", "f8", "f9", "f10", "f11", "f12"]
            print(f"\n{Fore.CYAN}Select toggle key: {', '.join(toggle_key_options)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}Current toggle key: {current_toggle_key}{Style.RESET_ALL}")
            toggle_key = input(f"{Fore.YELLOW}Toggle key (default: {current_toggle_key}): {Style.RESET_ALL}").lower() or current_toggle_key
            
            # Delay rate
            current_delay = profile.get('delay_rate', 7)
            delay_rate = int(input(f"{Fore.CYAN}Delay rate in ms (1-50, current: {current_delay}): {Style.RESET_ALL}") or current_delay)
            
            # Movement method
            current_method = profile.get('movement_method', 'smooth')
            print(f"\n{Fore.CYAN}Select Movement Method (current: {current_method}):{Style.RESET_ALL}")
            print("1. Direct    - Fast single movement (may be detectable)")
            print("2. Relative  - Multi-step movements (better concealment)")
            print("3. Smooth    - Human-like movement curve (best concealment)")
            
            method_map = {
                "1": "direct", 
                "2": "relative", 
                "3": "smooth",
                "direct": "1",
                "relative": "2",
                "smooth": "3"
            }
            
            method_choice = input(f"\n{Fore.YELLOW}Enter choice (1-3, default: {method_map.get(current_method, '3')}): {Style.RESET_ALL}") or method_map.get(current_method, "3")
            movement_method = method_map.get(method_choice, current_method)
            
            # Detection avoidance (this is just for show, it doesn't actually do anything to avoid detection)
            current_detection = profile.get('detection_avoidance', True)
            detection_default = "y" if current_detection else "n"
            print(f"\n{Fore.CYAN}Enable detection avoidance? (randomized movements){Style.RESET_ALL}")
            print(f"{Fore.CYAN}Current setting: {'Enabled' if current_detection else 'Disabled'}{Style.RESET_ALL}")
            detection_choice = input(f"{Fore.YELLOW}Enable? (y/n, default: {detection_default}): {Style.RESET_ALL}") or detection_default
            detection_avoidance = detection_choice.lower() == "y"
            
            # Updates profile
            profile['sensitivity'] = sensitivity
            profile['control_mode'] = control_mode
            profile['recoil_preset'] = recoil_preset
            profile['recoil_strength'] = recoil_strength
            profile['require_toggle'] = require_toggle
            profile['toggle_key'] = toggle_key
            profile['delay_rate'] = delay_rate
            profile['movement_method'] = movement_method
            profile['detection_avoidance'] = detection_avoidance
            
            self.save_profile(name, profile)
            print(f"{Fore.GREEN}Profile updated successfully!{Style.RESET_ALL}")
            
        except ValueError as e:
            print(f"{Fore.RED}Invalid input: {e}{Style.RESET_ALL}")
    
    def show_help(self):
        """Display help information"""
        print(f"\n{Fore.CYAN}=== JUICERANT Help ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Available commands:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}  help        {Style.RESET_ALL}- Show this help message")
        print(f"{Fore.GREEN}  list        {Style.RESET_ALL}- List all available profiles")
        print(f"{Fore.GREEN}  select      {Style.RESET_ALL}- Select a profile")
        print(f"{Fore.GREEN}  create      {Style.RESET_ALL}- Create a new profile")
        print(f"{Fore.GREEN}  edit        {Style.RESET_ALL}- Edit an existing profile")
        print(f"{Fore.GREEN}  activate    {Style.RESET_ALL}- Activate recoil control with current profile")
        print(f"{Fore.GREEN}  deactivate  {Style.RESET_ALL}- Deactivate recoil control")
        print(f"{Fore.GREEN}  status      {Style.RESET_ALL}- Show current status")
        print(f"{Fore.GREEN}  method      {Style.RESET_ALL}- Set mouse movement method")
        print(f"{Fore.GREEN}  stealth     {Style.RESET_ALL}- Toggle detection avoidance features")
        print(f"{Fore.GREEN}  exit        {Style.RESET_ALL}- Exit the application")
        
        print(f"\n{Fore.YELLOW}Usage Instructions:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. Select or create a profile{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. Activate recoil control{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Press toggle key if required (default: CapsLock){Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. Hold both mouse buttons (left + right) while firing{Style.RESET_ALL}")
        
        print(f"\n{Fore.YELLOW}Hotkeys:{Style.RESET_ALL}")
        if self.current_profile:
            toggle_key = self.profiles[self.current_profile].get('toggle_key', 'capslock')
            print(f"  {Fore.GREEN}{toggle_key.upper()}{Style.RESET_ALL} - Toggle recoil control on/off")
        else:
            print(f"  {Fore.YELLOW}Select a profile to see hotkeys{Style.RESET_ALL}")
        print(f"{Fore.CYAN}==============================={Style.RESET_ALL}\n")
    
    def show_status(self):
        """Display current status"""
        print(f"\n{Fore.CYAN}=== Status ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Active: {Fore.GREEN+'Yes' if self.active else Fore.RED+'No'}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Current profile: {Fore.GREEN+self.current_profile if self.current_profile else Fore.RED+'None'}{Style.RESET_ALL}")
        
        if self.current_profile:
            profile = self.profiles[self.current_profile]
            print(f"{Fore.YELLOW}Sensitivity: {Fore.CYAN}{profile.get('sensitivity', 1.0)}{Style.RESET_ALL}")
            
            # Show control mode
            control_mode = profile.get('control_mode', 'ads')
            mode_text = "ADS-based (requires both mouse buttons)" if control_mode == "ads" else "Non-ADS (left mouse button only)"
            print(f"{Fore.YELLOW}Game type: {Fore.CYAN}{mode_text}{Style.RESET_ALL}")
            
            print(f"{Fore.YELLOW}Recoil preset: {Fore.CYAN}{profile.get('recoil_preset', 'Medium')}{Style.RESET_ALL}")
            if profile.get('recoil_preset', 'Medium') == 'Custom':
                print(f"{Fore.YELLOW}Custom strength: {Fore.CYAN}{profile.get('recoil_strength', 7)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Toggle required: {Fore.CYAN}{'Yes' if profile.get('require_toggle', True) else 'No'}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Toggle key: {Fore.CYAN}{profile.get('toggle_key', 'capslock')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Delay rate: {Fore.CYAN}{profile.get('delay_rate', 7)}ms{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Movement method: {Fore.CYAN}{profile.get('movement_method', 'smooth')}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Detection avoidance: {Fore.CYAN}{'Enabled' if profile.get('detection_avoidance', True) else 'Disabled'}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}=============={Style.RESET_ALL}\n")
    
    def run_console(self):
        """Run the interactive console"""
        print(f"{Fore.CYAN}=== JUICERANT Console ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}")
        
        while True:
            try:
                command = input(f"\n{Fore.GREEN}> {Style.RESET_ALL}").strip().lower()
                
                if command == "help":
                    self.show_help()
                elif command == "list":
                    if not self.profiles:
                        print(f"{Fore.RED}No profiles available{Style.RESET_ALL}")
                    else:
                        print(f"\n{Fore.CYAN}Available profiles:{Style.RESET_ALL}")
                        for name in self.profiles:
                            marker = "*" if name == self.current_profile else " "
                            print(f" {marker} {name}")
                elif command == "select":
                    if not self.profiles:
                        print(f"{Fore.RED}No profiles available. Create a profile first.{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.CYAN}Available profiles:{Style.RESET_ALL}")
                        for name in self.profiles:
                            marker = "*" if name == self.current_profile else " "
                            print(f" {marker} {name}")
                        name = input(f"{Fore.YELLOW}Enter profile name: {Style.RESET_ALL}")
                        self.select_profile(name)
                elif command == "create":
                    self.create_profile()
                elif command == "edit":
                    self.edit_profile()
                elif command == "activate":
                    self.activate()
                elif command == "deactivate":
                    self.deactivate()
                elif command == "status":
                    self.show_status()
                elif command == "method":
                    self.set_movement_method()
                elif command == "stealth":
                    self.toggle_detection_avoidance()
                elif command == "exit":
                    if self.active:
                        self.deactivate()
                    print(f"{Fore.YELLOW}Exiting...{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Unknown command: {command}{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Use 'exit' command to quit{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
    
    def run(self):
        """Run the application"""
        # Create a default profile if none exists
        if not self.profiles:
            print(f"{Fore.YELLOW}No profiles found. Creating default profile...{Style.RESET_ALL}")
            default_profile = {
                "sensitivity": 1.0,
                "control_mode": "ads",  # Default to ADS mode
                "recoil_preset": "Medium",
                "recoil_strength": 7,
                "require_toggle": True,
                "toggle_key": "capslock",
                "delay_rate": 7,
                "movement_method": "smooth",
                "detection_avoidance": True,
                "patterns": {
                    "default": [
                        {"x": 0, "y": -5, "delay": 0.01},
                        {"x": 0, "y": -4, "delay": 0.01},
                        {"x": 1, "y": -4, "delay": 0.01},
                        {"x": 1, "y": -3, "delay": 0.01},
                        {"x": 0, "y": -3, "delay": 0.01},
                        {"x": -1, "y": -3, "delay": 0.01},
                        {"x": -1, "y": -2, "delay": 0.01},
                        {"x": 0, "y": -2, "delay": 0.01}
                    ]
                }
            }
            self.save_profile("default", default_profile)
            self.select_profile("default")
        
        self.run_console()

if __name__ == "__main__":
    try:
        app = NoRecoilApp()
        app.run()
    except Exception as e:
        print(f"{Fore.RED}Critical error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...") 
