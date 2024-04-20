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
    
    base64_encoded_public_key = base64.b64encode(public_key.encode()).decode()
    
    print("Encoded Public Key:", base64_encoded_public_key)

# Specify the path to your public key file
file_path = '/home/sdp/rsa.pub'

# Get the encoded key
base64_encoded_public_key = encode_key_to_base64(file_path)
print("Base64 Encoded Public Key:", base64_encoded_public_key)