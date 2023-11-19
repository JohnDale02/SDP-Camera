
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
import base64
import cv2
import subprocess
import tempfile
import os

def sign_verify():

    # Define the command and its arguments as a list
    tpm2_verify_command = [
        "tpm2_verifysignature",
        "-c",
        "public_key.pem",
        "-g",
        "sha256",
        "-s",
        "signature.file",
        "combined.file"
    ]

    try:
        # Execute the command
        result = subprocess.run(tpm2_verify_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        print("stdout:")
        print(result.stdout)
        print("stderr:")
        print(result.stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error: Command returned non-zero exit status {e.returncode}")
    except FileNotFoundError:
        print("Error: The tss2_verifysignature command was not found. Make sure it's in your system's PATH.")


   

print(sign_verify())
