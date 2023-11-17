import base64

def verify_signiture():
    # Base64 encoded content of your PEM file
    encoded_content = "ARYAAQALAAYAcgAAABAAEAgAAAAAAAEAvaHHo4zyskOAZT2cdEbHnH6K0/Wn2/55U5UVCr9NJAZqH6D8CwUkgHyEcyHEpsNsG2Pz/Wfp4twBXvY+54mPXdTCG+eoynY6Ua/iRMDGoicsc8acTcasP/lCZ/kWAsyl+4Zwxpiz79pZeqnervz3T80QQKFLE8Ri3rbse1R/AdUsKAQkRFcr/YSFjdJZVKbixBw9Xgs5LDFfO4N6j6wXVO1vRt/6WEkDyrBCVFtXgUArIW1N7+HWl0jf59du/93ZbVK0l33Y9HRRuGODonuB0UZp3xfOOO1bBl7fyq/Gzt1FV+zIEIukBivNoyG/cdGhYPLGD2xrsNadcUOgP5xCfw=="

    # Decode the Base64 content back to binary
    binary_content = base64.b64decode(encoded_content)

    # Write the binary content back to a PEM file
    output_file_path = 'recreated_public_key.pem'
    with open(output_file_path, 'wb') as file:
        file.write(binary_content)
    # verify_signature(image, time, location, signature, public_key)
            # Decrypt digital signiture with public key
            # Combine Image + Time + Location
            # Hash Combined data
            # Compare with hash
            # Return True or false