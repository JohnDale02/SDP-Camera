def print_first_last_bytes_of_avi(filepath):
    try:
        with open(filepath, 'rb') as file:
            # Read the entire file into a bytes object
            data = file.read()
            
            # Get the first 10 and last 10 bytes
            first_10_bytes = data[:10]
            last_10_bytes = data[-10:]
            
            print("First 10 bytes (hex):", first_10_bytes.hex())
            print("Last 10 bytes (hex):", last_10_bytes.hex())

    except FileNotFoundError:
        print(f"File not found: {filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
print_first_last_bytes_of_avi('C:\\Users\\John Dale\\Downloads\\7.avi')

