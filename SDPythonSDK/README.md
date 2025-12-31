# Govee Light Control (Python)

This repo contains a Stream Dock plugin that controls Govee devices (On/Off + Brightness) using the OpenAPI. It uses the Stream Dock Python SDK to communicate with the Stream Dock app over WebSocket.

## Features

- Device On/Off action (button)
- Brightness action (knob rotation)
- Device picker in the property inspector

## Project Structure

```
.
├── com.mirabox.streamdock.goveelightcontrol.sdPlugin/  # Plugin bundle (manifest, UI, assets)
├── src/                # Source code directory
│   ├── core/          # Core functionality modules
│   │   ├── action.py        # Action class, handles button events
│   │   ├── plugin.py        # Core plugin class, manages WebSocket connections
│   │   ├── logger.py        # Log management
│   │   └── action_factory.py # Action factory class
│   └── actions/       # Specific action implementations
├── requirements.txt   # Project dependencies
├── requirements-dev.txt # Packaging dependencies
├── main.py           # Main program entry
├── main.spec         # PyInstaller configuration file
├── scripts/package_mac.sh # Build a distributable macOS bundle
└── README.md         # Project documentation
```

## Development Environment Setup

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Activate virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Dev-in-place (symlink)

For local development, the plugin bundle is symlinked into the Stream Dock plugins folder. The bundle uses `plugin_mac.sh` to run `main.py` with the venv Python.

1. Create a symlink (macOS):
```bash
ln -s "$(pwd)/com.mirabox.streamdock.goveelightcontrol.sdPlugin" \
      "$HOME/Library/Application Support/HotSpot/StreamDock/plugins/"
```

2. Ensure `plugin_mac.sh` points to the venv Python:
```
venv/bin/python
```

3. Restart Stream Dock after changes.

## Plugin Development Guide

### Creating Custom Actions

1. Create a new action class in the `src/actions` directory:

```python
from src.core.action import Action

class Custom(Action):
    def __init__(self, action, context, settings, plugin):
        super().__init__(action, context, settings, plugin)
    
    def on_key_up(self, payload):
        # Handle button click event
        self.set_title("Button Clicked")
        self.set_state(0)
```

### Logging

```python
from src.core.logger import Logger

# Log information
Logger.info("Operation successful")
# Log error
Logger.error("Error occurred")
```

## Packaging and Distribution (macOS)

1. Install packaging dependency:
```bash
pip install -r requirements-dev.txt
```

2. Build the distributable bundle:
```bash
./scripts/package_mac.sh
```

3. The bundle is written to:
```
dist/com.mirabox.streamdock.goveelightcontrol.sdPlugin
```

## Note

If you encounter module not found errors, this is because `action_factory.py` uses `importlib.import_module` to dynamically load classes under `actions`, and `PyInstaller` statically analyzes code during packaging. If needed, add the missing modules to `hiddenimports` in `main.spec`.

## Development Standards

- Use type annotations to ensure code type safety
- Follow PEP 8 coding standards
- Write unit tests to ensure code quality
- Use the built-in logging system to record critical information

## License

This project is licensed under the MIT License. See the LICENSE file for details.
