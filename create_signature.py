import subprocess
import tempfile
import os
import base64 


def create_signature(digest):
    '''Takes in a digest; returns signature as base64 string'''
    
    # Write hash string to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_digest_file:  # create a temporary digest file where we put our digest for intput to sign
        temp_digest_file.write(digest)
        digest_file = temp_digest_file.name

    # Create a temporary file for the signature
    with tempfile.NamedTemporaryFile(delete=False) as temp_signature_file:  # create a temporary output file for the signature
        signature_file = temp_signature_file.name

    # Use the temporary files in the tpm2_sign command
    tpm2_sign_command = [
        "sudo",
        "tpm2",
        "sign",
        "-Q",
        "-c",
        "0x81010001",  # key memory location
        "-g", "sha256",
        "-d",   digest_file,
        "-f", "plain",
        "-s", "rsassa",
        "-o", signature_file
    ]

    # Execute the command
    result = subprocess.run(tpm2_sign_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    print("Signature stdout: ", result.stdout)
    print("Signature stderr: ", result.stderr)
    print("Exit Code:", result.returncode)

    # Delete the temporary hash file
    os.remove(digest_file)

    # Read and delete the temporary signature file
    signature = None
    if os.path.exists(signature_file):
        with open(signature_file, 'rb') as file:
            signature = file.read()
        os.remove(signature_file)

    if result.returncode == 0 and signature:
        # Binary signature
        
        #print("Signature:", signature)
        signature_string = base64.b64encode(signature).decode('utf-8')
        #print("Signature String:", signature_string)

        return signature_string
    else:
        raise Exception("Error in generating signature: " + result.stderr.decode())

