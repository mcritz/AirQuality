# AirQuality

A micropython project that displays current air conditions to an RGB pixel.

This example uses a [TinyPico](https://www.tinypico.com) which as everything you’ll need on the board without adding any extras. Other boards will need to confirm the hardware GPIO pins in code.

Update your config.json:

```json
{
  "url": "http://www.purpleair.com/json?show=60015",
  "ssid": "My WiFi Network Name",
  "password": "super secret password"
}
```
