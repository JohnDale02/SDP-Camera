import base64

# Specify the file path of your PEM file
file_path = 'public_key.pem'

# Read the file in binary mode
with open(file_path, 'rb') as file:
    binary_content = file.read()

# Encode the binary data to a Base64 string for easy handling and display
encoded_content = base64.b64encode(binary_content).decode('utf-8')
encoded_bytes = base64.b64encode(binary_content)
decoded = base64.b64decode(encoded_content)
assert binary_content == encoded_bytes

print(encoded_content)