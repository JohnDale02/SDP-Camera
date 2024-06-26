from pyfingerprint.pyfingerprint import PyFingerprint
import time

try:
    ## Change here: Update the port to '/dev/ttyAMA1' or the correct one for UART4
    f = PyFingerprint('/dev/ttyAMA5', 57600, 0xFFFFFFFF, 0x00000000)

    if (f.verifyPassword() == False):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

try:
    print('Waiting for finger...')
    while (f.readImage() == False):
        pass

    f.convertImage(0x01)
    #result = f.searchTemplate()
    #positionNumber = result[0]

    #if (positionNumber >= 0):
     #   print('Template already exists at position #' + str(positionNumber))
    #   exit(0)

    print('Remove finger...')
    time.sleep(2)
    print('Waiting for same finger again...')

    while (f.readImage() == False):
        pass

    f.convertImage(0x02)

    if (f.compareCharacteristics() == 0):
        raise Exception('Fingers do not match')

    f.createTemplate()
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
