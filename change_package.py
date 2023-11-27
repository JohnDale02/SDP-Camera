
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
