# ESP32-Real-Time-Sensor-Monitoring-Dashboard
A modern IoT monitoring system built with ESP32, MicroPython, HTML, CSS, and JavaScript for real-time sensor data visualization. The dashboard communicates directly with an ESP32 web server and displays live environmental and system metrics through an interactive cyber-themed interface.

Hardware Connections

| Sensor Module                      | Sensor Pin | ESP32 Pin | Power |
| ---------------------------------- | ---------- | --------- | ----- |
| **DHT22 (Temperature & Humidity)** | VCC        | 3.3V      | 3.3V  |
|                                    | GND        | GND       | -     |
|                                    | DATA       | GPIO 4    | -     |
| **MAX30102 (Heart Rate Sensor)**   | VIN/VCC    | 3.3V      | 3.3V  |
|                                    | GND        | GND       | -     |
|                                    | SDA        | GPIO 21   | I2C   |
|                                    | SCL        | GPIO 22   | I2C   |
| **HC-SR04 (Ultrasonic Sensor)**    | VCC        | 5V (VIN)  | 5V    |
|                                    | GND        | GND       | -     |
|                                    | TRIG       | GPIO 5    | -     |
|                                    | ECHO       | GPIO 18*  | -     |
------------------------------------------------------------------------



                    +------------------+
                    |      ESP32       |
                    |                  |
                    | GPIO4   <-- DHT22
                    | GPIO21  <-> MAX30102 SDA
                    | GPIO22  <-> MAX30102 SCL
                    | GPIO5   --> HC-SR04 TRIG
                    | GPIO18  <-- HC-SR04 ECHO
                    |                  |
                    +--------+---------+
                             |
                             |
                        Wi-Fi Network
                             |
                             |
                  +--------------------+
                  | Web Dashboard      |
                  | HTML/CSS/JS        |
                  | Real-Time Charts   |
                  | Alerts & Logging   |
                  +--------------------+
