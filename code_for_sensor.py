import machine
import network
import time
import socket
import json
import dht
import gc

# ==========================================
# CONFIGURATION: Change these to your details
# ==========================================
WIFI_SSID = "Pk_webs"
WIFI_PASSWORD = "77777777"

# PIN CONFIGURATIONS
DHT_PIN = 4      # Humidity & Temperature (DHT11 Data Line)
TRIG_PIN = 5     # HC-SR04 Ultrasonic Trigger
ECHO_PIN = 18    # HC-SR04 Ultrasonic Echo
BUZZER_PIN = 19  # Hardware Transducer Pin

# ==========================================
# HARDWARE INITIALIZATION
# ==========================================
# 1. DHT11 Initialization
sensor = None
try:
    sensor = dht.DHT11(machine.Pin(DHT_PIN))
    print("✔ DHT11 Hardware Handler Initialized.")
except Exception as e:
    print("⚠ DHT11 initialization bypassed:", e)

# 2. HC-SR04 Ultrasonic Pins
trig = machine.Pin(TRIG_PIN, machine.Pin.OUT)
echo = machine.Pin(ECHO_PIN, machine.Pin.IN)
trig.value(0)

# 3. Buzzer Pin
buzzer = machine.Pin(BUZZER_PIN, machine.Pin.OUT)
buzzer.value(0)

# 4. MAX30102 / I2C Core Placeholder Reference
# Defaults to normal human resting heart rate if biometric hardware is initializing
latest_heartrate = 72.0 

# ==========================================
# SENSOR UTILITIES
# ==========================================
def read_distance():
    """Reads distance from HC-SR04 safely with a non-blocking timeout."""
    try:
        # Send a 10-microsecond trigger pulse
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        
        # Measure duration of the echo return pulse (max wait ~25000us)
        duration = machine.time_pulse_us(echo, 1, 25000)
        
        if duration < 0:
            return 400.0  # Return max out-of-range value on timeout
            
        # Calculate speed of sound step down (cm)
        distance = (duration * 0.0343) / 2
        return round(distance, 1)
    except Exception:
        return 400.0

# ==========================================
# NETWORK SETUP (WI-FI)
# ==========================================
wlan = network.WLAN(network.STA_IF)

if wlan.isconnected():
    wlan.disconnect()
wlan.active(False)
time.sleep(0.5) 

wlan.active(True)
print("Connecting to Wi-Fi...")
wlan.connect(WIFI_SSID, WIFI_PASSWORD)

timeout = 10
while not wlan.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1

if wlan.isconnected():
    ip_address = wlan.ifconfig()[0]
    print("\n--- WI-FI CONNECTED SUCCESSFULLY ---")
    print("ESP32 IP Address:", ip_address)
    print("👉 USE CONFIG PANEL OR SET IP AT TOP OF HTML INTERFACE 👈")
    print("------------------------------------\n")
else:
    print("❌ Wi-Fi connection failed. Check your SSID and Password.")
    raise SystemExit

# ==========================================
# WEB SERVER SOCKET SETUP
# ==========================================
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

print("Polling Engine Server listening on port 80... Ready for Dashboard v4.0 requests.\n")

# ==========================================
# MAIN ROUTING ENGINE LOOP
# ==========================================
while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        
        # 1. JSON Data Node Route
        if "GET /json" in request:
            temp = 24.5
            humid = 50.0
            
            if sensor is not None:
                try:
                    sensor.measure()
                    temp = sensor.temperature()
                    humid = sensor.humidity()
                except Exception as e:
                    print("Failed to poll live DHT11 frame:", e)
            
            # Fetch active physical metrics
            live_distance = read_distance()
            
            # Extract signal level metrics natively from Wi-Fi stack
            rssi_val = -55
            signal_pct = 80
            try:
                # Basic check for MicroPython firmware variant support
                if hasattr(wlan, 'status'):
                    rssi_val = wlan.status('rssi')
                    # Calculate metric conversion: maps RSSI to 0-100% scale
                    if rssi_val == 0: signal_pct = 0
                    elif rssi_val >= -50: signal_pct = 100
                    elif rssi_val <= -100: signal_pct = 0
                    else: signal_pct = int((rssi_val + 100) * 2)
            except:
                pass

            # Calculate actual current free RAM heap ceiling
            gc.collect()
            free_ram_kb = int(gc.mem_free() / 1024)

            # Construct exact data frame required by Dashboard v4.0
            payload = {
                "temperature": float(temp),
                "humidity": float(humid),
                "distance": float(live_distance),
                "heartrate": float(latest_heartrate),
                "wifi_signal": signal_pct,
                "rssi": rssi_val,
                "free_heap": free_ram_kb
            }
            
            response_body = json.dumps(payload)
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Connection: close\r\n\r\n"
            )
            
            conn.send(response_headers)
            conn.send(response_body)
            
        # 2. Remote Command Buzzer Route
        elif "POST /buzzer" in request or "OPTIONS /buzzer" in request:
            # Handle Preflight OPTIONS and POST CORS safely
            response_headers = (
                "HTTP/1.1 200 OK\r\n"
                "Access-Control-Allow-Origin: *\r\n"
                "Access-Control-Allow-Methods: POST, GET, OPTIONS\r\n"
                "Access-Control-Allow-Headers: Content-Type\r\n"
                "Connection: close\r\n\r\n"
            )
            conn.send(response_headers)
            
            if "POST /buzzer" in request:
                print("⚡ Buzzer diagnostic trigger received!")
                # Sound alert briefly without stalling network engine sockets
                buzzer.value(1)
                time.sleep_ms(250)
                buzzer.value(0)
                
        else:
            conn.send("HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n")
            
        conn.close()
        
    except Exception as e:
        print("Server frame processing error:", e)
        if 'conn' in locals():
            try:
                conn.close()
            except:
                pass