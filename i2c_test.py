import smbus
import time

bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1
device_address = 0x48  # Replace with your device's address

while True:
    data = bus.read_byte(device_address)
    print("Data received:", data)
    time.sleep(1)  # Delay for a second
