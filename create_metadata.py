

def create_metadata(camera_number : str, time_data : str, location_data : str, signature_string : bytes):
    '''Cretes dictionary with all metadata; Strings for number, time, location, base64 (bytes) for signature'''

    metadata = {}
    metadata['CameraNumber'] = camera_number
    metadata['Time'] = time_data
    metadata['Location'] = location_data
    metadata['Signature'] = signature_string

    return metadata

#print(create_metadata(1, "10:45", "east of ur moms house", "SIGNEDJOHNIDFN"))
