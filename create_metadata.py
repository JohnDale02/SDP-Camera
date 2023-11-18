def create_metadata(camera_number, time_data, location_data, signiture):

    metadata = {}
    metadata['CameraNumber'] = camera_number
    metadata['Time'] = time_data
    metadata['Location'] = location_data
    metadata['Signature'] = signiture

    return metadata

#print(create_metadata(1, "10:45", "east of ur moms house", "SIGNEDJOHNIDFN"))
