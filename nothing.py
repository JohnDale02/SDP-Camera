import time

def sleep():
# Duration for the program to sleep in seconds
    sleep_duration = 10

    print(f"Program starts. Sleeping for {sleep_duration} seconds.")

    # Sleep for the specified duration
    time.sleep(sleep_duration)

    print("Program finished.")
