# from ublox_gps import UbloxGps
# import spidev
# import time

# # Configure your SPI settings
# spi_bus = 0  # Replace with the appropriate SPI bus number
# spi_device = 0  # Replace with the appropriate SPI device (chip select) number
# spi_speed = 500000  # Replace with the desired SPI speed (Hz)

# # Initialize SPI
# spi = spidev.SpiDev()
# spi.open(spi_bus, spi_device)
# spi.max_speed_hz = spi_speed

# gps = UbloxGps(spi_device)

# try:
#     print("Listening for UBX Messages.")
#     while True:
#         try:
#             coords = gps.geo_coords()
#             print(coords.lon, coords.lat)
#         except (ValueError, IOError) as err:
#             print(err)
#         time.sleep(1)

# finally:
#     spi.close()


from ublox_gps import UbloxGps
import serial
# Can also use SPI here - import spidev
# I2C is not supported

port = serial.Serial('/dev/serial0', baudrate=38400, timeout=1)
gps = UbloxGps(port)

def run():
  
  try: 
    print("Listenting for UBX Messages.")
    while True:
      try: 
        coords = gps.geo_coords()
        print(coords.lon, coords.lat)
      except (ValueError, IOError) as err:
        print(err)
  
  finally:
    port.close()

if __name__ == '__main__':
  run()