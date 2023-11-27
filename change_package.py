# New file under Ulobx-gps

sfeI2cWrapper.py

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



# Modify the ublox_gps.py file init

def __init__(self, hard_port=None):
    if hard_port is None:
        self.hard_port = serial.Serial("/dev/serial0/", 38400, timeout=1)
    elif isinstance(hard_port, spidev.SpiDev):
        sfeSpi = sfeSpiWrapper(hard_port)
        self.hard_port = sfeSpi
    elif isinstance(hard_port, sfeI2cWrapper):
        self.hard_port = hard_port
    else:
        # Handle other types of connections or raise an error
        pass
