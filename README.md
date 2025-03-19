# No-Recoil Assistant

A versatile no-recoil assistant that works with all mice brands. This application helps compensate for weapon recoil in first-person shooter games by applying counter-movements to your mouse when you fire, with enhanced detection avoidance features.

## Features

- **Universal Compatibility**: Works with all mice brands and models
- **Enhanced Anti-Detection**: Multiple movement methods to avoid detection
- **Advanced Humanization**: Bezier curve movement paths and human-like behavior patterns
- **User-Friendly Interface**: Colorful console interface with intuitive commands
- **Multiple Profiles**: Load and manage profiles from JSON files for different games
- **Configurable Patterns**: Fine-tune recoil patterns for different weapons
- **Game-Specific Control Modes**: Support for both ADS and non-ADS games
- **Adjustable Settings**: Sensitivity, recoil strength, and movement methods
- **Hotkey Support**: Customizable toggle keys

https://imgur.com/I49BEMw

## Installation

### Prerequisites

- Python 3.7+ installed
- Required Python packages (install using pip):
  - pynput
  - keyboard
  - colorama

### Setup

1. Clone this repository or download the source code
2. Install the required packages:

```
pip install -r requirements.txt
```

3. Run the application using the provided batch file:

```
run.bat
```

Or manually:

```
cd no-recoil
python src/main.py
```

## Usage

### Console Commands

The application features a colorful, user-friendly console interface with the following commands:

- `help` - Show help information
- `list` - List all available profiles
- `select` - Select a profile
- `create` - Create a new profile
- `edit` - Edit an existing profile
- `activate` - Activate no-recoil with current profile
- `deactivate` - Deactivate no-recoil
- `status` - Show current status
- `method` - Change mouse movement method
- `stealth` - Toggle detection avoidance features
- `exit` - Exit the application

### Control Modes

The application supports two different control modes:

1. **ADS Mode** (Aim Down Sights):
   - Used for games where you typically right-click to aim (like Apex Legends, Rainbow Six Siege)
   - Recoil control activates only when both left and right mouse buttons are pressed
   - Set with `"control_mode": "ads"` in your profile

2. **Non-ADS Mode**:
   - Used for games where you primarily fire without aiming down sights (like CS:GO, Valorant)
   - Recoil control activates when only the left mouse button is pressed
   - Set with `"control_mode": "non_ads"` in your profile

### Anti-Detection Features

The application includes several advanced features to avoid detection by anti-cheat systems:

1. **Multiple Movement Methods**:
   - `Direct` - Fast, simple movements (basic)
   - `Relative` - Multi-step movements (better concealment)
   - `Smooth` - Human-like movements with acceleration curves (best concealment)

2. **Advanced Humanization**:
   - Bezier curve mouse movements that mimic natural hand movement
   - Micro-pauses and timing variations like a human player
   - Progressive fatigue simulation (slight timing changes during extended firing)
   - Occasional skipped compensation to simulate human error

3. **Smart Activation**:
   - Variable activation delays when you start firing
   - Natural-looking mouse movement recovery after firing stops
   - Randomized compensation intensity within human-like ranges

4. **Process Protection**:
   - Dynamic process priority adjustments to avoid detection
   - Low resource utilization to prevent performance flags

### Recoil Presets

The application includes several preset recoil strength levels:

- `Low` - Minimal recoil compensation
- `Medium` - Moderate recoil compensation
- `High` - Strong recoil compensation
- `Ultra` - Very strong recoil compensation
- `Insanity` - Extreme recoil compensation
- `Custom` - Use your own recoil_strength value

### Profile Configuration

Profiles are stored as JSON files in the `src/profiles` directory. Each profile can include:

- `name` - Name of the profile
- `sensitivity` - Adjusts overall mouse sensitivity
- `control_mode` - Sets the activation mode ("ads" or "non_ads")
- `recoil_preset` - Preset recoil strength level ("Low", "Medium", "High", etc.)
- `recoil_strength` - Custom multiplier for recoil compensation intensity
- `require_toggle` - Whether toggle key is required (true/false)
- `toggle_key` - Keyboard key to toggle the script on/off
- `delay_rate` - The delay between recoil compensation movements in milliseconds
- `movement_method` - Method used for mouse movement ("direct", "relative", or "smooth")
- `detection_avoidance` - Enable/disable randomization features
- `patterns` - Collection of recoil patterns (x, y movements and delays)

### Example Profile Structure

#### ADS Game Profile (Apex Legends)
```json
{
    "name": "apex",
    "sensitivity": 1.2,
    "control_mode": "ads",
    "recoil_preset": "High",
    "recoil_strength": 7,
    "require_toggle": true,
    "toggle_key": "capslock",
    "delay_rate": 5,
    "movement_method": "relative",
    "detection_avoidance": true,
    "patterns": {
        "default": [
            {"x": 0, "y": -5, "delay": 0.01},
            {"x": 0, "y": -4, "delay": 0.01},
            ...
        ],
        "r301": [
            ...
        ]
    }
}
```

#### Non-ADS Game Profile (CS:GO)
```json
{
    "name": "csgo",
    "sensitivity": 0.9,
    "control_mode": "non_ads",
    "recoil_preset": "High",
    "recoil_strength": 8,
    "require_toggle": true,
    "toggle_key": "capslock",
    "delay_rate": 6,
    "movement_method": "relative",
    "detection_avoidance": true,
    "patterns": {
        "default": [
            {"x": 0, "y": -6, "delay": 0.01},
            {"x": 0, "y": -5, "delay": 0.01},
            ...
        ],
        "ak47": [
            ...
        ]
    }
}
```

### Creating Custom Patterns

To create an effective recoil pattern:

1. Study the recoil pattern of the weapon in your game
2. Create a sequence of mouse movements that counteract that pattern
3. Adjust the `delay` values to match the fire rate
4. Fine-tune `sensitivity` and `recoil_strength` for your setup
5. Experiment with different movement methods for your game

## Legal Disclaimer

This software is provided for educational purposes only. Using this software may violate the terms of service of certain games, and could result in your account being banned. The author is not responsible for any consequences resulting from the use of this software.

## Troubleshooting

If you encounter issues:

1. Make sure you're running the script as administrator (especially on Windows)
2. Try different movement methods (some games detect certain methods)
3. Adjust the sensitivity and recoil strength
4. Enable or disable detection avoidance based on your game
5. Ensure your profile is properly configured for your game
6. Check that the correct control mode is set for your game type
7. If detection is a concern, try enabling the bezier curve movement feature

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is released under the MIT License. 
