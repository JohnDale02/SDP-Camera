# Function for veryfying the image, metadata and digital signiture for the image

# verify_signature(image, time, location, signature, public_key)
        # Decrypt digital signiture with public key
        # Combine Image + Time + Location
        # Hash Combined data
        # Compare with hash
        # Return True or false