def create_metadata(time_data, location_data, signiture):

    metadata = {}
    metadata['Time'] = time_data
    metadata['Location'] = location_data
    metadata['Signature'] = signiture

    return metadata

print(create_metadata("10:45", "east of ur moms house", "SIGNEDJOHNIDFN"))