from pyfingerprint.pyfingerprint import PyFingerprint

def get_fingerprint():
    try:
        ## Change here: Update the port to '/dev/ttyAMA4'
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
        result = f.searchTemplate()

        positionNumber = result[0]
        accuracyScore = result[1]

        if (positionNumber == -1):
            print('No match found!')
            return -1
        else:
            print('Found template at position #' + str(positionNumber))
            print('The accuracy score is: ' + str(accuracyScore))
            return positionNumber

    except Exception as e:
        print('Operation failed!')
        print('Exception message: ' + str(e))
        exit(1)


print(get_fingerprint())