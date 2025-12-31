import uuid
import requests
from src.core.action import Action
from src.core.logger import Logger


class Govee(Action):
    API_KEY = ""
    DEVICE_MAC = "29:0C:C7:09:9E:1E:42:81"
    DEVICE_SKU = "H61B8"
    CAPABILITY_TYPE = "devices.capabilities.on_off"
    CAPABILITY_INSTANCE = "powerSwitch"
    BASE_URL = "https://openapi.api.govee.com/router/api/v1"
    DEFAULT_TIMEOUT_SECS = 10

    def __init__(self, action: str, context: str, settings: dict, plugin):
        super().__init__(action, context, settings, plugin)
        self.settings = settings or {}
        self._api_key = self._get_api_key()
        self._device = self._get_device()
        self._sku = self._get_sku()
        self._device_name = self._get_device_name()
        self._power = self.settings.get("power", "off")
        self._sync_display()
        Logger.info(f"[Govee] Initialized with context {context}")

    def on_did_receive_settings(self, settings: dict):
        self.settings = settings or {}
        self._api_key = self._get_api_key()
        self._device = self._get_device()
        self._sku = self._get_sku()
        self._device_name = self._get_device_name()
        self._power = self.settings.get("power", self._power)
        self._sync_display()

    def on_key_up(self, payload: dict):
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

    def _has_config(self) -> bool:
        if not self._api_key:
            Logger.error("[Govee] Missing API key")
            return False
        if not self._device or self._device.startswith("YOUR_"):
            Logger.error("[Govee] Missing device id (device MAC)")
            return False
        if not self._sku or self._sku.startswith("YOUR_"):
            Logger.error("[Govee] Missing device sku")
            return False
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
                    "type": self.CAPABILITY_TYPE,
                    "instance": self.CAPABILITY_INSTANCE,
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
            Logger.error(f"[Govee] Request failed: {exc}")
            return False

        try:
            data = response.json()
        except ValueError:
            data = None

        if response.status_code != 200:
            Logger.error(f"[Govee] HTTP {response.status_code}: {response.text}")
            return False
        if isinstance(data, dict):
            code = data.get("code")
            if code not in (None, 200, 0):
                Logger.error(f"[Govee] API error {code}: {data.get('message')}")
                return False

        Logger.info(f"[Govee] Power set to {value}")
        return True

    def _sync_display(self):
        is_on = self._power == "on"
        self.set_state(1 if is_on else 0)
        state_text = "On" if is_on else "Off"
        if self._device_name:
            display_name = self._device_name
            if " " in display_name:
                display_name = display_name.replace(" ", "\n", 1)
            self.set_title(f"{display_name}\n{state_text}")
        else:
            self.set_title(state_text)

    def _update_settings(self, **updates):
        current = dict(self.settings) if isinstance(self.settings, dict) else {}
        current.update(updates)
        self.set_settings(current)
