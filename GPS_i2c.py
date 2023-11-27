import smbus
import time
from ublox_gps import UbloxGps  # Replace with your actual library import

# Initialize the I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Define the I2C address of the GPS module
gps_address = 0x42

# Create a GPS module instance with the specified address
gps = UbloxGps(bus, gps_address)

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                # Replace with appropriate methods from your library.
                geo = gps.geo_coords()
                print("Latitude: {0:.6f}, Longitude: {1:.6f}".format(geo.lat, geo.lon))
            except (ValueError, IOError) as err:
                print(err)
            
            time.sleep(1)

    finally:
        print("Disabling GPS module.")
        gps.cleanup()

if __name__ == '__main__':
    run()
