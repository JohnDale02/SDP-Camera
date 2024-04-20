import base64

def encode_key_to_base64(file_path):
    # Open and read the public key file
    with open(file_path, 'r') as file:
        public_key = file.read()
    
    # The public key file typically starts with '-----BEGIN PUBLIC KEY-----'
    # and ends with '-----END PUBLIC KEY-----'. We need to remove these headers
    # and any newlines or extra spaces.
    start_marker = "-----BEGIN PUBLIC KEY-----"
    end_marker = "-----END PUBLIC KEY-----"
    
    # Strip headers/footers and replace newlines
    encoded_key = public_key.replace(start_marker, '').replace(end_marker, '').strip()
    
    # Base64 decode, then re-encode to ensure it's in clean base64 format
    # This step depends on the formatting of your key file. If it's already base64-encoded,
    # this decode-encode step can be adjusted or skipped as necessary.
    key_bytes = base64.b64decode(encoded_key.encode())
    clean_base64_encoded_key = base64.b64encode(key_bytes).decode('utf-8')
    
    return clean_base64_encoded_key

# Specify the path to your public key file
file_path = '/home/sdp/rsa.pub'

# Get the encoded key
base64_encoded_public_key = encode_key_to_base64(file_path)
print("Base64 Encoded Public Key:", base64_encoded_public_key)