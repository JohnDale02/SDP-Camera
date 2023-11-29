import sys
import os

# Add the directory containing your module to the Python path
module_path = os.path.expanduser('~/Qwiic_Ublox_Gps_Py/ublox_gps_module')
sys.path.append(module_path)

# Now you can import your module and class
from ublox_gps import UbloxGps

# Use the class
gps = UbloxGps(...)


import spidev

from ublox_gps import UbloxGps

port = spidev.SpiDev()
gps = UbloxGps(port)

def run():

    try:
        print("Listening for UBX Messages")
        while True:
            try:
                geo = gps.geo_coords()
                print("Longitude: ", geo.lon) 
                print("Latitude: ", geo.lat)
                print("Heading of Motion: ", geo.headMot)
            except (ValueError, IOError) as err:
                print(err)

    finally:
        port.close()


if __name__ == '__main__':
    run()
