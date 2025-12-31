import time
import uuid
import requests
from src.core.action import Action
from src.core.logger import Logger


class Brightness(Action):
    API_KEY = ""
    DEVICE_MAC = "29:0C:C7:09:9E:1E:42:81"
    DEVICE_SKU = "H61B8"
    CAPABILITY_TYPE = "devices.capabilities.range"
    CAPABILITY_INSTANCE = "brightness"
    POWER_TYPE = "devices.capabilities.on_off"
    POWER_INSTANCE = "powerSwitch"
    BASE_URL = "https://openapi.api.govee.com/router/api/v1"
    DEFAULT_TIMEOUT_SECS = 10
    MIN_BRIGHTNESS = 1
    MAX_BRIGHTNESS = 100
    BRIGHTNESS_STEP = 5

    def __init__(self, action: str, context: str, settings: dict, plugin):
        super().__init__(action, context, settings, plugin)
        self.settings = settings or {}
        self._api_key = self._get_api_key()
        self._device = self._get_device()
        self._sku = self._get_sku()
        self._device_name = self._get_device_name()
        self._brightness = self._get_brightness()
        self._power = self._get_power()
        self._step = self._get_step()
        self._supports_brightness = self._get_supports_brightness()
        self._warned_no_brightness = False
        self._last_rotate_at = 0.0
        self._sync_display()
        Logger.info(f"[Brightness] Initialized with context {context}")

    def on_did_receive_settings(self, settings: dict):
        self.settings = settings or {}
        self._api_key = self._get_api_key()
        self._device = self._get_device()
        self._sku = self._get_sku()
        self._device_name = self._get_device_name()
        self._brightness = self._get_brightness()
        self._power = self._get_power()
        self._step = self._get_step()
        self._supports_brightness = self._get_supports_brightness()
        self._warned_no_brightness = False
        self._sync_display()

    def on_dial_rotate(self, payload: dict):
        self._last_rotate_at = time.monotonic()
        Logger.info(f"[Brightness] dialRotate payload: {payload}")
        delta = self._extract_delta(payload)
        if delta == 0:
            return
        if not self._supports_brightness:
            if not self._warned_no_brightness:
                Logger.warning("[Brightness] Device does not support brightness control")
                self._warned_no_brightness = True
            self.show_alert()
            return
        if not self._has_config():
            self.show_alert()
            return

        step = self._step * delta
        new_value = max(
            self.MIN_BRIGHTNESS,
            min(self.MAX_BRIGHTNESS, self._brightness + step),
        )
        if new_value == self._brightness:
            return
        if self._set_brightness(new_value):
            self._brightness = new_value
            self._update_settings(brightness=new_value)
            self._sync_display()
            self.show_ok()
        else:
            self.show_alert()

    def on_dial_down(self, payload: dict):
        if time.monotonic() - self._last_rotate_at < 0.35:
            Logger.info(f"[Brightness] Ignoring dialDown near rotate: {payload}")
            return
        if self._looks_like_rotate_payload(payload):
            Logger.info(f"[Brightness] Ignoring dialDown rotate payload: {payload}")
            return
        Logger.info(f"[Brightness] dialDown payload: {payload}")
        target = "off" if self._power == "on" else "on"
        if not self._has_config():
            self.show_alert()
            return
        if self._set_power(target):
            self._power = target
            self._update_settings(power=target)
            self._sync_display()
            self.show_ok()
        else:
            self.show_alert()

    def _get_api_key(self) -> str:
        key = self.settings.get("api_key") or self.API_KEY
        return key.strip() if isinstance(key, str) else ""

    def _get_device(self) -> str:
        device = self.settings.get("device") or self.DEVICE_MAC
        return device.strip() if isinstance(device, str) else ""

    def _get_sku(self) -> str:
        sku = self.settings.get("sku") or self.DEVICE_SKU
        return sku.strip() if isinstance(sku, str) else ""

    def _get_device_name(self) -> str:
        name = self.settings.get("device_name") or ""
        return name.strip() if isinstance(name, str) else ""

    def _get_brightness(self) -> int:
        value = self.settings.get("brightness", 50)
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = 50
        return max(self.MIN_BRIGHTNESS, min(self.MAX_BRIGHTNESS, value))

    def _get_power(self) -> str:
        power = self.settings.get("power", "on")
        return power if power in ("on", "off") else "on"

    def _get_step(self) -> int:
        value = self.settings.get("step", self.BRIGHTNESS_STEP)
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = self.BRIGHTNESS_STEP
        return max(1, min(self.MAX_BRIGHTNESS, value))

    def _get_supports_brightness(self) -> bool:
        value = self.settings.get("supports_brightness")
        if value is None:
            return self._sku != "SameModeGroup"
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "y")
        return bool(value)

    def _looks_like_rotate_payload(self, payload: dict) -> bool:
        if not isinstance(payload, dict):
            return False
        for key in ("ticks", "delta", "rotation", "dialRotation"):
            if key in payload:
                return True
        return False

    def _extract_delta(self, payload: dict) -> int:
        if not isinstance(payload, dict):
            return 0
        for key in ("ticks", "delta"):
            if key in payload:
                try:
                    return int(payload[key])
                except (TypeError, ValueError):
                    return 0
        for key in ("rotation", "dialRotation"):
            if key in payload:
                rotation = payload[key]
                if isinstance(rotation, (int, float)):
                    return int(rotation)
                if isinstance(rotation, str):
                    value = rotation.lower()
                    if value.startswith("c") or "right" in value:
                        return 1
                    if value.startswith("a") or "left" in value:
                        return -1
        return 0

    def _has_config(self) -> bool:
        if not self._api_key:
            Logger.error("[Brightness] Missing API key")
            return False
        if not self._device or self._device.startswith("YOUR_"):
            Logger.error("[Brightness] Missing device id (device MAC)")
            return False
        if not self._sku or self._sku.startswith("YOUR_"):
            Logger.error("[Brightness] Missing device sku")
            return False
        return True

    def _set_brightness(self, value: int) -> bool:
        url = f"{self.BASE_URL}/device/control"
        headers = {
            "Govee-API-Key": self._api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "requestId": uuid.uuid4().hex,
            "payload": {
                "sku": self._sku,
                "device": self._device,
                "capability": {
                    "type": self.CAPABILITY_TYPE,
                    "instance": self.CAPABILITY_INSTANCE,
                    "value": value,
                },
            },
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT_SECS,
            )
        except requests.RequestException as exc:
            Logger.error(f"[Brightness] Request failed: {exc}")
            return False

        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code != 200:
            Logger.error(f"[Brightness] HTTP {response.status_code}: {response.text}")
            return False
        if isinstance(data, dict):
            code = data.get("code")
            if code not in (None, 200, 0):
                Logger.error(f"[Brightness] API error {code}: {data.get('message')}")
                return False

        Logger.info(f"[Brightness] Brightness set to {value}")
        return True

    def _set_power(self, value: str) -> bool:
        url = f"{self.BASE_URL}/device/control"
        headers = {
            "Govee-API-Key": self._api_key,
            "Content-Type": "application/json",
        }
        power_value = 1 if value == "on" else 0
        payload = {
            "requestId": uuid.uuid4().hex,
            "payload": {
                "sku": self._sku,
                "device": self._device,
                "capability": {
                    "type": self.POWER_TYPE,
                    "instance": self.POWER_INSTANCE,
                    "value": power_value,
                },
            },
        }
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.DEFAULT_TIMEOUT_SECS,
            )
        except requests.RequestException as exc:
            Logger.error(f"[Brightness] Power request failed: {exc}")
            return False

        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code != 200:
            Logger.error(f"[Brightness] Power HTTP {response.status_code}: {response.text}")
            return False
        if isinstance(data, dict):
            code = data.get("code")
            if code not in (None, 200, 0):
                Logger.error(f"[Brightness] Power API error {code}: {data.get('message')}")
                return False

        Logger.info(f"[Brightness] Power set to {value}")
        return True

    def _sync_display(self):
        self.set_state(1 if self._power == "on" else 0)
        if self._device_name:
            display_name = self._device_name
            if " " in display_name:
                display_name = display_name.replace(" ", "\n", 1)
            self.set_title(f"{display_name}\n{self._brightness}%")
        else:
            self.set_title(f"{self._brightness}%")

    def _update_settings(self, **updates):
        current = dict(self.settings) if isinstance(self.settings, dict) else {}
        current.update(updates)
        self.set_settings(current)
