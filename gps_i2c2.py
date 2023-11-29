import smbus
import time

class sfeI2cWrapper(object):
    def __init__(self, bus_number, address):
        self.bus = smbus.SMBus(bus_number)
        time.sleep(0.5)  # Delay after initializing SMBus
        self.address = address

    def read(self, num_bytes=32):
        """
        Read bytes from the I2C device.
        Adjust num_bytes if necessary to match the expected data length.
        """
        try:
            data = self.bus.read_i2c_block_data(self.address, 0, num_bytes)
            return bytes(data)
        except IOError:
            return None

    def write(self, data):
        if isinstance(data, bytes):
            data = list(data)
        self.bus.write_i2c_block_data(self.address, 0, data)
        return True

# GPS I2C setup
i2c_bus_number = 1
i2c_address = 0x42

# Create an instance of the I2C wrapper
gps_i2c = sfeI2cWrapper(i2c_bus_number, i2c_address)

def run():
    print("Listening for GPS data")
    try:
        while True:
            data = gps_i2c.read(32)  # Read 32 bytes of data; adjust as needed
            if data:
                print("Received data:", data)
            else:
                print("No GPS data received. Trying again...")
            time.sleep(1)
    except KeyboardInterrupt:
        print("GPS data reading stopped by user.")
    finally:
        print("Finished reading GPS data.")

if __name__ == '__main__':
    run()
