const $local = false, $back = false,
    $dom = {
        main: $('.sdpi-wrapper'),
        apiKey: $('#apiKey'),
        deviceSelect: $('#deviceSelect'),
        deviceId: $('#deviceId'),
        deviceSku: $('#deviceSku'),
        loadDevices: $('#loadDevices'),
        stepRow: $('#stepRow'),
        stepSize: $('#stepSize'),
    },
    $propEvent = {
        didReceiveSettings(data) {
            const settings = data.settings || {};
            $dom.stepRow.style.display = ($action || '').endsWith('.brightness') ? '' : 'none';
            if (settings.api_key !== undefined) {
                $dom.apiKey.value = settings.api_key;
            }
            if (settings.device !== undefined) {
                $dom.deviceId.value = settings.device;
            }
            if (settings.sku !== undefined) {
                $dom.deviceSku.value = settings.sku;
            }
            if (settings.step !== undefined) {
                $dom.stepSize.value = settings.step;
            }
        },
        sendToPropertyInspector(data) {
            console.log("sendToPropertyInspector", data);
        },
        didReceiveGlobalSettings(data) {
            console.log("didReceiveGlobalSettings", data);
        },
    };

    $dom.loadDevices.addEventListener('click', async () => {
    const apiKey = $dom.apiKey.value.trim();
    if (!apiKey) {
        alert('Enter an API key first.');
        return;
    }
    $dom.loadDevices.disabled = true;
    $dom.loadDevices.textContent = 'Loading...';

    try {
        const resp = await fetch(
            'https://openapi.api.govee.com/router/api/v1/user/devices',
            { headers: { 'Govee-API-Key': apiKey } }
        );
        const data = await resp.json();
        if (!resp.ok || (data && data.code !== 200)) {
            console.error('Failed to load devices', data);
            alert('Failed to load devices. Check API key and try again.');
            return;
        }
        const devices = Array.isArray(data.data) ? data.data : [];
        devices.sort((a, b) => {
            const nameA = (a.deviceName || '').toLowerCase();
            const nameB = (b.deviceName || '').toLowerCase();
            if (nameA < nameB) return -1;
            if (nameA > nameB) return 1;
            return 0;
        });
        $dom.deviceSelect.innerHTML = '';
        devices.forEach(item => {
            const caps = Array.isArray(item.capabilities) ? item.capabilities : [];
            const supportsBrightness = caps.some(cap => {
                return cap.type === 'devices.capabilities.range' &&
                    cap.instance === 'brightness';
            });
            const option = document.createElement('option');
            option.value = `${item.device}|${item.sku}`;
            option.textContent = `${item.deviceName} (${item.sku})`;
            option.dataset.deviceName = item.deviceName || '';
            option.dataset.supportsBrightness = supportsBrightness ? 'true' : 'false';
            $dom.deviceSelect.appendChild(option);
        });
        if (devices.length === 0) {
            const option = document.createElement('option');
            option.value = '';
            option.textContent = 'No devices found';
            $dom.deviceSelect.appendChild(option);
        }
        if (typeof $settings !== 'undefined' && $settings.device && $settings.sku) {
            const existingValue = `${$settings.device}|${$settings.sku}`;
            $dom.deviceSelect.value = existingValue;
            const selected = $dom.deviceSelect.options[$dom.deviceSelect.selectedIndex];
            if (selected) {
                $dom.deviceId.value = $settings.device;
                $dom.deviceSku.value = $settings.sku;
                $settings.device_name = selected.dataset.deviceName || '';
                $settings.supports_brightness = selected.dataset.supportsBrightness === 'true';
            }
        }
    } catch (err) {
        console.error('Device load failed', err);
        alert('Error loading devices. Check your connection.');
    } finally {
        $dom.loadDevices.disabled = false;
        $dom.loadDevices.textContent = 'Load Devices';
    }
});

$dom.deviceSelect.addEventListener('change', () => {
    const value = $dom.deviceSelect.value;
    if (!value) {
        return;
    }
    const [device, sku] = value.split('|');
    const selected = $dom.deviceSelect.options[$dom.deviceSelect.selectedIndex];
    const deviceName = selected ? (selected.dataset.deviceName || '') : '';
    const supportsBrightness = selected ? (selected.dataset.supportsBrightness === 'true') : false;
    $dom.deviceId.value = device || '';
    $dom.deviceSku.value = sku || '';
    if (typeof $settings !== 'undefined') {
        $settings.device = device || '';
        $settings.sku = sku || '';
        $settings.device_name = deviceName;
        $settings.supports_brightness = supportsBrightness;
    }
});

$dom.apiKey.addEventListener('input', () => {
    if (typeof $settings === 'undefined') {
        return;
    }
    $settings.api_key = $dom.apiKey.value.trim();
});

$dom.stepSize.addEventListener('input', () => {
    if (typeof $settings === 'undefined') {
        return;
    }
    $settings.step = $dom.stepSize.value.trim();
});
