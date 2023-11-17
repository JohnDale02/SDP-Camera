import subprocess
import tempfile
import os

def sign_hash(hash_string):
    # Write hash string to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_hash_file:  # create a temporary hash file where we put our hash for signing
        temp_hash_file.write(bytearray.fromhex(hash_string))
        temp_hash_file_path = temp_hash_file.name

    # Create a temporary file for the signature
    with tempfile.NamedTemporaryFile(delete=False) as temp_signature_file:  # create a temporary output file for the signature
        temp_signature_file_path = temp_signature_file.name

    # Use the temporary files in the tpm2_sign command
    tpm2_sign_command = [
        "tpm2_sign",
        "-c", "0x81010001",
        "-g", "sha256",
        "-o", temp_signature_file_path,
        temp_hash_file_path
    ]

    # Execute the command
    result = subprocess.run(tpm2_sign_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read and delete the temporary signature file
    signature = None
    if os.path.exists(temp_signature_file_path):
        with open(temp_signature_file_path, 'rb') as file:
            signature = file.read()
        os.remove(temp_signature_file_path)

    # Delete the temporary hash file
    os.remove(temp_hash_file_path)

    if result.returncode == 0 and signature:
        # Convert the binary signature to a hexadecimal string
        signature_hex = signature.hex()
        return signature_hex
    else:
        raise Exception("Error in generating signature: " + result.stderr.decode())

