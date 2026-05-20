# Water Meter Pulse Counter — Direct Raspberry Pi GPIO (No ESP, No Wi-Fi)

A simple, reliable water consumption monitor using an inductive proximity sensor wired directly to a Raspberry Pi. No ESP32, no Wi-Fi, no cloud.

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Why?

Most DIY water meter projects use an ESP8266/ESP32 with ESPHome to read pulses from the meter and send them to Home Assistant over Wi-Fi. This works, but adds complexity and a wireless failure point.

If your Raspberry Pi (running Home Assistant) is close enough to run a cable to the water meter, you can skip the ESP entirely and read the sensor pulses straight from the Pi's GPIO pins.

**Inspired by** [Pieter Brinkman's water sensor guide](https://www.pieterbrinkman.com/2022/02/02/build-a-cheap-water-usage-sensor-using-esphome-home-assistant-and-a-proximity-sensor/) — simplified by removing the ESP and Wi-Fi layer.

## Architecture

```
┌──────────────┐        3-wire cable          ┌──────────────────┐
│  Water Meter │  ◄── proximity sensor ──►    │   Raspberry Pi   │
│              │      (5V, GND, Signal)       │  (Home Assistant)│
└──────────────┘                              └──────────────────┘
```

## Photos

<!-- TODO: Add your own photos here -->

![Overview of the complete setup](images/overview.jpg)
*The full setup: sensor on the meter, cable run, voltage divider at the Pi.*

![Proximity sensor mounted on water meter](images/sensor-on-meter.jpg)
*LJ18A3-8Z/BX proximity sensor zip-tied to the water meter.*

![Wiring at the sensor end](images/rj45-sensor-end.jpg)
*Sensor wires connected to the cable.*

![Voltage divider at the Raspberry Pi end](images/voltage-divider.jpg)
*Simple 1kΩ + 2kΩ voltage divider before the GPIO pin.*

![Home Assistant Energy Dashboard showing water consumption](images/ha-dashboard.jpg)
*Water consumption visible in the Home Assistant Energy Dashboard.*

## Bill of Materials

| Item | Approx. Cost | Notes |
|------|-------------|-------|
| LJ18A3-8Z/BX proximity sensor (5V) | ~€4 | Must be the 5V version with built-in resistor |
| 3-wire cable | ~€2-5 | Any cable with at least 3 conductors, length as needed |
| 1kΩ + 2kΩ resistors | ~€0.10 | For 5V→3.3V voltage divider |
| **Total** | **~€5-10** | |

## Wiring

### Wire Assignment

Only 3 wires are needed:

| Wire | Function | Sensor Wire Color | Pi Connection |
|------|----------|-------------------|---------------|
| 1 | +5V Power | Brown/Orange (VIN) | Pi 5V (physical pin 2 or 4) |
| 2 | Signal | Black | Pi GPIO17 (physical pin 11) via voltage divider |
| 3 | Ground | Blue | Pi GND (physical pin 6 or 9) |

### Voltage Divider (Required!)

The Pi GPIO pins are **3.3V only**. The LJ18A3 outputs 5V. You need a simple resistor divider at the Pi end:

```
Sensor Signal (5V) ──── [1kΩ] ────┬──── GPIO17 (3.3V safe)
                                   │
                                 [2kΩ]
                                   │
                                  GND
```

This gives: 5V × 2kΩ / (1kΩ + 2kΩ) = 3.33V ✓

### Wiring Diagram

```
                    AT THE WATER METER                          AT THE RASPBERRY PI
                    ==================                          ==================

  LJ18A3-8Z/BX                                                 Raspberry Pi GPIO
  ┌───────────┐         3-wire cable                           ┌─────────────┐
  │           │                                                 │             │
  │ VIN (5V) ─┼──── Wire 1 ────────────────────────────────────┼─ 5V (pin 2) │
  │           │                                                 │             │
  │ Signal   ─┼──── Wire 2 ──────────────── [1kΩ] ───┬─────────┼─ GPIO17     │
  │           │                                       │         │  (pin 11)   │
  │           │                                     [2kΩ]       │             │
  │           │                                       │         │             │
  │ GND      ─┼──── Wire 3 ──────────────────────────┴─────────┼─ GND (pin 6)│
  │           │                                                 │             │
  └───────────┘                                                 └─────────────┘
```

## Software Setup

The included Python script reads GPIO pulses and publishes water consumption to Home Assistant via MQTT. It handles debouncing and fast flow rates reliably.

See [`water_meter.py`](water_meter.py) for the full implementation.

### Prerequisites

```bash
pip install gpiod paho-mqtt
```

### Run as a systemd service

```bash
sudo cp water-meter.service /etc/systemd/system/
sudo systemctl enable water-meter
sudo systemctl start water-meter
```

## Sensor Placement

The proximity sensor detects the small metal disc embedded in your water meter's spinning wheel. Each full rotation = 1 pulse = 1 liter (check your meter — this varies).

1. Open a tap and watch the meter's small wheel spin
2. Hold the sensor flat against the meter face, over the spinning wheel
3. The red LED on the sensor lights up each time the magnet passes
4. Secure with zip ties or velcro

## Comparison with ESP-based Approach

| | ESP + Wi-Fi (traditional) | Direct GPIO (this project) |
|---|---|---|
| Controller | ESP8266/ESP32 | None — Pi GPIO |
| Communication | Wi-Fi | Wired (direct cable) |
| Software | ESPHome | HA integration or Python |
| Reliability | Depends on Wi-Fi | Rock solid |
| Components | Sensor + ESP + USB power | Sensor + 2 resistors |
| Cost | ~€10 | ~€5-10 |
| Latency | ~1-6s (Wi-Fi polling) | Instant (hardware interrupt) |

## Troubleshooting

- **No pulses detected**: Check voltage divider output with a multimeter (should read ~3.3V when sensor triggers). Verify sensor LED blinks when water flows.
- **Double counting**: Increase debounce time in the Python script or add a hardware capacitor (100nF) across the GPIO pin.
- **Signal noise over long cable**: Add a 10kΩ pull-down resistor at the Pi end, or use a shielded cable.
- **Sensor doesn't detect magnet**: Try repositioning — the sensing distance is ~8mm. Some meters have weaker magnets.

## License

MIT — do whatever you want with this.

## Credits

- Original ESP-based approach: [Pieter Brinkman](https://www.pieterbrinkman.com/2022/02/02/build-a-cheap-water-usage-sensor-using-esphome-home-assistant-and-a-proximity-sensor/)
- Simplified wired design: this project
