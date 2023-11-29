import spidev
import time

spi = spidev.SpiDev()
spi.open(0, 0)  # Open bus 0, device 0 (CE0)
spi.max_speed_hz = 500000  # Set speed

try:
    # Send some data and read the response
    response = spi.xfer2([0x76])  # Example command
    print("Response:", response)
finally:
    spi.close()
