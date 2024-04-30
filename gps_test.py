import serial
from datetime import datetime, timedelta
import time 

def parse_nmea_sentence(sentence):
    """Parse GNRMC sentence to extract latitude, longitude, time, and date."""
    parts = sentence.split(',')

    # Process only RMC sentences as they contain all required data
    if parts[0] == '$GNRMC':
        # Check if the data is valid
        valid = parts[2] == 'A'  # Data is valid if the status is 'A'

        if valid:
            # Parse time
            time_value = parts[1]
            time_object = datetime.strptime(time_value, "%H%M%S.%f")
            new_time_object = time_object - timedelta(hours=5)
            formatted_time = new_time_object.strftime("%H:%M:%S")

            # Parse latitude
            lat_value = float(parts[3])
            lat_hemisphere = parts[4]
            lat_degrees = int(lat_value / 100)
            lat_minutes = lat_value - (lat_degrees * 100)
            latitude = lat_degrees + (lat_minutes / 60)
            if lat_hemisphere == 'S':
                latitude *= -1

            # Parse longitude
            lon_value = float(parts[5])
            lon_hemisphere = parts[6]
            lon_degrees = int(lon_value / 100)
            lon_minutes = lon_value - (lon_degrees * 100)
            longitude = lon_degrees + (lon_minutes / 60)
            if lon_hemisphere == 'W':
                longitude *= -1

            # Parse date
            date_str = parts[9]
            date_object = datetime.strptime(date_str, "%d%m%y")
            formatted_date = date_object.strftime("%Y-%m-%d")

            return latitude, longitude, formatted_time, formatted_date

    return None, None, None, None

def read_gps_data():
    
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=5)
    try: 
        start_time = time.time()
        while True:
            sentence = ser.readline().decode('utf-8', errors='ignore').strip()
            if sentence:
                latitude, longitude, formatted_time, formatted_date = parse_nmea_sentence(sentence)
                print(f"Latitude: {latitude}, Longitude: {longitude}, Time: {formatted_time}, Date: {formatted_date}")
            if time.time() - start_time > ser.timeout:
                print("Timeout reached. No GPS data received.")
                break
    except KeyboardInterrupt:
        print("Program terminated!")
    finally:
        ser.close()
    return "None", "None", "None"

    

read_gps_data()