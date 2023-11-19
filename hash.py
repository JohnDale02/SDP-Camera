import hashlib

def calculate_sha256_hash(data):
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data)
    
    return sha256_hash.digest()


with open('combined.file', 'rb') as combined:
    combined_data = combined.read()

digest = calculate_sha256_hash(combined_data)

with open('digest.file', 'wb') as digest_file:
    digest_file.write(digest)






