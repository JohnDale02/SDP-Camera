import sys
from pyfingerprint.pyfingerprint import PyFingerprint

if len(sys.argv) < 2:
    print("Usage: python script.py <position_number>")
    exit(1)

positionNumber = int(sys.argv[1])  # Convert command line argument to integer

try:
    ## Initialize fingerprint sensor
    f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

    if (f.verifyPassword() == False):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

try:
    ## Attempt to delete the fingerprint template at the specified position
    if (f.deleteTemplate(positionNumber) == True):
        print('Template deleted successfully!')
    else:
        print('Failed to delete template!')

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
