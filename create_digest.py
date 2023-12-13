import hashlib


def create_digest(combined_data):
    '''Takes in combined data as a byte object; returns digest'''

    sha256_hash = hashlib.sha256()
    sha256_hash.update(combined_data)

    return sha256_hash.digest()

