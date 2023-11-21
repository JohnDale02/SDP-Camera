from ublox_gps import UbloxGps
import spidev
import time

# Configure your SPI settings
spi_bus = 0  # Replace with the appropriate SPI bus number
spi_device = 0  # Replace with the appropriate SPI device (chip select) number
spi_speed = 500000  # Replace with the desired SPI speed (Hz)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(spi_bus, spi_device)
spi.max_speed_hz = spi_speed

gps = UbloxGps(spi)

try:
    print("Listening for UBX Messages.")
    while True:
        try:
            coords = gps.geo_coords()
            print(coords.lon, coords.lat)
        except (ValueError, IOError) as err:
            print(err)
        time.sleep(1)

finally:
    spi.close()