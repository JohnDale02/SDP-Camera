import subprocess
import tempfile
import os
import base64 
import cv2


def hash(image_name): # will output hashed data to a file
    '''Takes in a hash; returns base64 encoded signature'''
    
    image = cv2.imread(image_name)
    time = "2023-10-29 14:30:00"
    location = "Latitude: 40.7128, Longitude: -74.0060"

    tpm2_hash_command = ['tpm2_hash',
                        '-C', 'e',
                        '-g', 'sha256', 
                        '-o', 'digest.file', 
                        '-t', 'ticket.bin', 
                        'combined.file'
                        ]

    # Execute the command
    result = subprocess.run(tpm2_hash_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")

    # Print stdout
    print("stdout:")
    print(result.stdout)

    # Print stderr
    print("stderr:")
    print(result.stderr)


