def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Paths to your .pem files
file_path_1 = 'public_key.pem'
file_path_2 = 'recreated_public_key.pem'

# Read the contents of both files
content_1 = read_file(file_path_1)
content_2 = read_file(file_path_2)

print(content_1)
print(content_2)

# Compare the contents
if content_1 == content_2:
    print("The files are the same.")
else:
    print("The files are different.")