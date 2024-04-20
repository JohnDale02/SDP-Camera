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
    
    print("Encoded Public Key:", encoded_key)

# Specify the path to your public key file
file_path = '/home/sdp/rsa.pub'

# Get the encoded key
base64_encoded_public_key = encode_key_to_base64(file_path)
print("Base64 Encoded Public Key:", base64_encoded_public_key)