

def create_metadata(fingerprint: str, camera_number : str, time_data : str, location_data : str, signature_string : bytes):
    '''Cretes dictionary with all metadata; Strings for number, time, location, base64 (bytes) for signature'''

    metadata = {}
    metadata['Fingerprint'] = fingerprint
    metadata['CameraNumber'] = camera_number
    metadata['Time'] = time_data
    metadata['Location'] = location_data
    metadata['Signature'] = signature_string

    return metadata


