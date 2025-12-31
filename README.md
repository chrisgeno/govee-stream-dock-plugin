# Govee Light Control for Stream Dock

I built this because the existing generic Govee Control plugin on https://vsdinside.key123.vip/ did not work on a MAC and the only other repo had been deleted by its original creator. I'm only supporting MAC for this plugin right now as that is all I use.

I built this for my setup in as generic a way as possible, as bug reports come in from other configurations I'll do my best to get them fixed. 

This was built for a generic Basicolor stream dock knockoff from amazon with 6 lcd buttons and 3 knobs and uses the Govee open api for basic functions.


Features:
- Device On/Off action (button)
- Brightness action (knob rotation)
- Device picker in the property inspector

Known Issues:
- The Brightness Knob does not function properly with groups. It should work with individual devices.



## Repo Layout

```
SDPythonSDK/  # Plugin source, bundle, and packaging scripts
```

## Development (dev-in-place)

1. Create a venv and install deps:
```bash
python3 -m venv SDPythonSDK/venv
SDPythonSDK/venv/bin/python -m pip install -r SDPythonSDK/requirements.txt
```

2. Symlink the plugin bundle into Stream Dock:
```bash
ln -s "~/GIT/StreamDock-Plugin-SDK/SDPythonSDK/com.mirabox.streamdock.goveelightcontrol.sdPlugin" \
      "/Users/christophergeno/Library/Application Support/HotSpot/StreamDock/plugins/"
```

3. Ensure `SDPythonSDK/com.mirabox.streamdock.goveelightcontrol.sdPlugin/plugin_mac.sh` points to the venv Python.

4. Restart Stream Dock.

Logs are written to `SDPythonSDK/logs/plugin.log`.

## Packaging (macOS)

The distributable build uses PyInstaller to bundle Python and all dependencies into a single macOS binary.
End users do not need a venv or `requests` installed.

1. Install packaging dependency:
```bash
SDPythonSDK/venv/bin/python -m pip install -r SDPythonSDK/requirements-dev.txt
```

2. Build:
```bash
cd SDPythonSDK
./scripts/package_mac.sh
```

3. The bundle is written to:
```
SDPythonSDK/dist/com.mirabox.streamdock.goveelightcontrol.sdPlugin
```

To install, copy that folder into:
`~/Library/Application Support/HotSpot/StreamDock/plugins`

Restart Stream Dock after installing.
