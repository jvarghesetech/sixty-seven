# Wiring up the physical NFC tag

This turns tapping your phone on an NFC sticker (stuck to your water bottle)
into a call to `POST /log`.

## 1. Run the server somewhere your phone can reach

For local testing on the same Wi-Fi network:

```
python app.py
```

Find your Mac's LAN IP with `ipconfig getifaddr en0`, e.g. `192.168.1.23`.
For real use away from home, deploy the Docker image (see `Dockerfile`) to a
small host (Fly.io, Railway, a Raspberry Pi, etc.) so it has a stable URL.

## 2. Set an API token

```
export WATER_API_TOKEN="pick-a-long-random-string"
```

Set the same value in the Shortcut in step 4.

## 3. Create the Shortcuts automation

1. Open **Shortcuts** app → **Automation** tab → **+** → **Create Personal Automation**.
2. Choose **NFC** → **Scan** → tap your water bottle's NFC tag.
3. Turn **Run Immediately** on (so it fires without a confirmation prompt).

## 4. Add the action

Add a **Get Contents of URL** action:

- URL: `http://<your-server>:5000/log`
- Method: `POST`
- Headers: `X-API-Token` = the same value as `WATER_API_TOKEN`
- Request Body: `JSON`, empty object `{}` (or `{"tag_id": "default"}` if you
  set up multiple tags per `/tags`)

Optionally add a **Show Notification** action after it, showing
`Logged 💧 (Cups Today: )` using the response's `cups` field so you get instant
feedback when you tap.

## 5. Test it

Tap the tag, then check `http://<your-server>:5000/` — the dashboard should
show one more cup for today.
