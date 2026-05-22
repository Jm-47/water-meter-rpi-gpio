#!/usr/bin/env python3
"""
Water meter pulse counter for Raspberry Pi GPIO.

Reads pulses from an LJ18A3-8Z/BX proximity sensor connected to a GPIO pin
and publishes the count to Home Assistant via MQTT (with auto-discovery).

Usage:
    python3 water_meter.py

Environment variables (optional):
    MQTT_HOST       - MQTT broker host (default: localhost)
    MQTT_PORT       - MQTT broker port (default: 1883)
    MQTT_USER       - MQTT username (default: none)
    MQTT_PASSWORD   - MQTT password (default: none)
    GPIO_PIN        - GPIO pin number (default: 17)
    DEBOUNCE_MS     - Debounce time in milliseconds (default: 50)
    STATE_FILE      - Path to persist total count across restarts
"""

import json
import os
import signal
import sys
import time

import gpiod
import paho.mqtt.client as mqtt

# Configuration from environment
MQTT_HOST = os.environ.get("MQTT_HOST", "localhost")
MQTT_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USER", "")
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD", "")
GPIO_CHIP = os.environ.get("GPIO_CHIP", "/dev/gpiochip0")
GPIO_PIN = int(os.environ.get("GPIO_PIN", "17"))
DEBOUNCE_MS = int(os.environ.get("DEBOUNCE_MS", "50"))
STATE_FILE = os.environ.get("STATE_FILE", "/var/lib/water-meter/total_liters")

# MQTT topics
DISCOVERY_TOPIC = "homeassistant/sensor/water_meter_total/config"
STATE_TOPIC = "homeassistant/sensor/water_meter_total/state"
ATTR_TOPIC = "homeassistant/sensor/water_meter_total/attributes"


def load_state() -> int:
    """Load persisted total liter count from disk."""
    try:
        with open(STATE_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


def save_state(total: int) -> None:
    """Persist total liter count to disk."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        f.write(str(total))


def publish_discovery(client: mqtt.Client) -> None:
    """Publish MQTT auto-discovery config for Home Assistant."""
    config = {
        "name": "Water Meter Total",
        "unique_id": "water_meter_rpi_gpio_total",
        "state_topic": STATE_TOPIC,
        "json_attributes_topic": ATTR_TOPIC,
        "unit_of_measurement": "L",
        "device_class": "water",
        "state_class": "total_increasing",
        "icon": "mdi:water",
        "device": {
            "identifiers": ["water_meter_rpi_gpio"],
            "name": "Water Meter (GPIO)",
            "model": "LJ18A3-8Z/BX + Raspberry Pi",
            "manufacturer": "DIY",
        },
    }
    client.publish(DISCOVERY_TOPIC, json.dumps(config), retain=True)


def main():
    total_liters = load_state()
    print(f"Starting water meter counter. Loaded state: {total_liters} L")

    # MQTT setup
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    connected = False

    def on_connect(client, userdata, flags, reason_code, properties=None):
        nonlocal connected
        if reason_code == 0:
            print("MQTT connected successfully")
            connected = True
        else:
            print(f"MQTT connection failed: {reason_code}")

    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()

    # Wait for connection
    for _ in range(50):
        if connected:
            break
        time.sleep(0.1)

    if not connected:
        print("ERROR: Could not connect to MQTT broker")
        sys.exit(1)

    # Publish discovery and initial state
    publish_discovery(client)
    client.publish(STATE_TOPIC, str(total_liters), retain=True)
    print(f"Published discovery and initial state: {total_liters} L")

    # GPIO setup
    chip = gpiod.Chip(GPIO_CHIP)
    line_request = gpiod.request_lines(
        GPIO_CHIP,
        consumer="water_meter",
        config={GPIO_PIN: gpiod.LineSettings(edge_detection=gpiod.line.Edge.RISING)},
    )

    last_event_ms = 0
    pulses_since_save = 0

    # Graceful shutdown
    def shutdown(signum, frame):
        print(f"\nShutting down. Total: {total_liters} L")
        save_state(total_liters)
        client.publish(STATE_TOPIC, str(total_liters), retain=True)
        client.disconnect()
        line_request.release()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print(f"Listening for pulses on GPIO{GPIO_PIN} (debounce: {DEBOUNCE_MS}ms)")

    while True:
        if line_request.wait_edge_events(timeout=10):
            events = line_request.read_edge_events()
            for event in events:
                now_ms = event.timestamp_ns // 1_000_000

                # Debounce
                if now_ms - last_event_ms < DEBOUNCE_MS:
                    continue

                last_event_ms = now_ms
                total_liters += 1
                pulses_since_save += 1

                # Publish to MQTT
                client.publish(STATE_TOPIC, str(total_liters), retain=True)
                client.publish(
                    ATTR_TOPIC,
                    json.dumps({"last_pulse": time.strftime("%Y-%m-%dT%H:%M:%S")}),
                )

                # Persist every 10 pulses to reduce SD card writes
                if pulses_since_save >= 10:
                    save_state(total_liters)
                    pulses_since_save = 0

                print(f"Pulse! Total: {total_liters} L")


if __name__ == "__main__":
    main()
