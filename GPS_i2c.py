import smbus
import time
from ublox_gps import UbloxGps  # Replace with your actual library import

import smbus

class sfeI2cWrapper(object):
    """
    sfeI2cWrapper

    Wrapper for I2C communication.

    :param bus_number: The I2C bus number to use (0, 1, etc.)
    :param address:    The I2C address of the device.
    :return:           The sfeI2cWrapper object.
    :rtype:            Object
    """

    def __init__(self, bus_number, address):
        self.bus = smbus.SMBus(bus_number)
        self.address = address

    def read(self, num_bytes=1):
        """
        Read bytes from the I2C device.

        :param num_bytes: The number of bytes to read.
        :return:          The read bytes.
        :rtype:           bytes
        """
        data = self.bus.read_i2c_block_data(self.address, 0, num_bytes)
        return bytes(data)

    def write(self, data):
        """
        Write bytes to the I2C device.

        :param data: Data to write (bytes or list of integers).
        :return:     True on completion.
        :rtype:      boolean
        """
        if isinstance(data, bytes):
            data = list(data)
        self.bus.write_i2c_block_data(self.address, 0, data)
        return True


# GPS I2C setup
i2c_bus_number = 1
i2c_address = 0x42

# Create an instance of the I2C wrapper
gps_i2c = sfeI2cWrapper(i2c_bus_number, i2c_address)

# Create an instance of the UbloxGps class with the I2C wrapper
gps = UbloxGps(hard_port=gps_i2c)

def run():
    try:
        print("Listening for UBX Messages")
        while True:
            try:
                # Replace with appropriate methods from your library.
                geo = gps.geo_coords()
                if geo is not None:
                    print("Latitude: {0:.6f}, Longitude: {1:.6f}".format(geo.lat, geo.lon))
                else:
                    print("No GPS data received. Trying again...")
            except (ValueError, IOError) as err:
                print("Error:", err)
            
            time.sleep(1)

    finally:
        print("Finished reading GPS data.")

if __name__ == '__main__':
    run()