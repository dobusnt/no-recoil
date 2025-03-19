import os
import json
import shutil

class ConfigManager:
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self._create_default_config()
        else:
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        default_config = {
            "last_profile": None,
            "auto_start": False,
            "start_minimized": False,
            "check_updates": True,
            "profiles_directory": os.path.join(os.path.dirname(__file__), 'profiles')
        }
        
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_setting(self, key, default=None):
        """Get a setting value"""
        return self.config.get(key, default)
    
    def set_setting(self, key, value):
        """Set a setting value"""
        self.config[key] = value
        self._save_config()
    
    def get_profiles_directory(self):
        """Get the profiles directory path"""
        profiles_dir = self.config.get('profiles_directory')
        if not profiles_dir:
            profiles_dir = os.path.join(os.path.dirname(__file__), 'profiles')
            self.config['profiles_directory'] = profiles_dir
            self._save_config()
            
        # Ensure directory exists
        if not os.path.exists(profiles_dir):
            os.makedirs(profiles_dir)
            
        return profiles_dir
    
    def set_profiles_directory(self, directory):
        """Set a new profiles directory"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        old_dir = self.get_profiles_directory()
        
        # Copy existing profiles to new directory if needed
        if os.path.exists(old_dir) and old_dir != directory:
            for filename in os.listdir(old_dir):
                if filename.endswith('.json'):
                    src_file = os.path.join(old_dir, filename)
                    dst_file = os.path.join(directory, filename)
                    shutil.copy2(src_file, dst_file)
        
        self.config['profiles_directory'] = directory
        self._save_config()
        
    def backup_profiles(self, backup_dir=None):
        """Backup all profiles to a backup directory"""
        if backup_dir is None:
            backup_dir = os.path.join(os.path.dirname(__file__), 'backups')
            
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
            
        profiles_dir = self.get_profiles_directory()
        if not os.path.exists(profiles_dir):
            return
            
        # Create timestamp for backup
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_subdir = os.path.join(backup_dir, f"backup_{timestamp}")
        os.makedirs(backup_subdir)
        
        # Copy all profiles to backup
        for filename in os.listdir(profiles_dir):
            if filename.endswith('.json'):
                src_file = os.path.join(profiles_dir, filename)
                dst_file = os.path.join(backup_subdir, filename)
                shutil.copy2(src_file, dst_file)
                
        print(f"Profiles backed up to: {backup_subdir}")
        return backup_subdir
    
    def import_profile(self, filepath):
        """Import a profile from a file"""
        if not os.path.exists(filepath):
            print(f"Profile file not found: {filepath}")
            return False
            
        try:
            # Read the profile
            with open(filepath, 'r') as f:
                profile_data = json.load(f)
                
            # Get profile name from filename
            profile_name = os.path.splitext(os.path.basename(filepath))[0]
            
            # Save to profiles directory
            profiles_dir = self.get_profiles_directory()
            dst_file = os.path.join(profiles_dir, f"{profile_name}.json")
            
            with open(dst_file, 'w') as f:
                json.dump(profile_data, f, indent=4)
                
            print(f"Profile '{profile_name}' imported successfully")
            return True
        except Exception as e:
            print(f"Error importing profile: {e}")
            return False
            
    def export_profile(self, profile_name, export_dir):
        """Export a profile to a file"""
        profiles_dir = self.get_profiles_directory()
        src_file = os.path.join(profiles_dir, f"{profile_name}.json")
        
        if not os.path.exists(src_file):
            print(f"Profile '{profile_name}' not found")
            return False
            
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        dst_file = os.path.join(export_dir, f"{profile_name}.json")
        
        try:
            shutil.copy2(src_file, dst_file)
            print(f"Profile '{profile_name}' exported to: {dst_file}")
            return True
        except Exception as e:
            print(f"Error exporting profile: {e}")
            return False 