import subprocess
import tempfile
import os
import base64 


def sign_hash(hash_string):
    '''Takes in a hash; returns base64 encoded signature'''
    
    # Write hash string to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_hash_file:  # create a temporary hash file where we put our hash for signing
        temp_hash_file.write(hash_string)
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
        # Binary signature
        print("Signature:", signature)
        signature_base64 = base64.b64encode(signature).decode('utf-8')
        print("Signature64:", signature_base64)

        return signature_base64
    else:
        raise Exception("Error in generating signature: " + result.stderr.decode())

