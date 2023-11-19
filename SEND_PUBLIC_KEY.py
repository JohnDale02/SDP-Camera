import base64


def are_files_equal(file1_path, file2_path):
    try:
        # Open both files in binary mode
        with open(file1_path, 'rb') as file1, open(file2_path, 'rb') as file2:
            # Read the contents of both files
            content1 = file1.read()
            content2 = file2.read()

            # Compare the contents byte by byte
            if content1 == content2:
                return True
            else:
                return False
    except Exception as e:
        # Handle any errors that may occur while reading or comparing files
        print(f"Error: {e}")
        return False
    

# Read the PEM file and convert it to a string
with open('public_key.pem', 'rb') as pem_file:
    pem_data = pem_file.read()
    print("Pem Data", pem_data)
    
    pem_string = base64.b64encode(pem_data).decode('utf-8')
    print("Pem string to be sent: ", pem_string)

# Store the PEM string in your database

# ... Code to insert pem_string into your database ...

# Retrieve the PEM string from the database
# For this example, let's assume you have retrieved it into the variable 'pem_string_from_db'

# Convert the PEM string back to bytes
pem_data_from_db = base64.b64decode(pem_string)

# Recreate the PEM file from the bytes
with open('recreated_public_key.pem', 'wb') as pem_file:
    pem_file.write(pem_data_from_db)
    print("Recreated PEM data", pem_data_from_db)

print("Check recreated_public_key.pem vs public_key.pem")
print("Are they equal: " , print(are_files_equal("recreated_public_key.pem", "public_key.pem")))


