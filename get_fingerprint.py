from pyfingerprint.pyfingerprint import PyFingerprint

try:
    ## Change here: Update the port to '/dev/ttyAMA1'
    f = PyFingerprint('/dev/ttyAMA1', 57600, 0xFFFFFFFF, 0x00000000)

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
    result = f.searchTemplate()

    positionNumber = result[0]
    accuracyScore = result[1]

    if (positionNumber == -1):
        print('No match found!')
    else:
        print('Found template at position #' + str(positionNumber))
        print('The accuracy score is: ' + str(accuracyScore))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
