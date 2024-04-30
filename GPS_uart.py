import serial
from datetime import datetime, timedelta
import time 

'''
def parse_nmea_sentence(sentence):
    """Parse GNGGA or GNRMC sentence to extract latitude and longitude."""
    parts = sentence.split(',')

    #if parts[0] in ['$GNGGA', '$GNRMC']:
    if parts[0] in ['$GNGGA']:
        # Check if the data is valid
        if parts[0] == '$GNGGA' and parts[6] != '0':
            valid = True
        elif parts[0] == '$GNRMC' and parts[2] == 'A':
            valid = True
        else:
            valid = False
        #print(f"valid: {valid}")
        if valid:
            time_value = parts[1]

            # Time string from the NMEA sentence
            nmea_time_str = time_value

            # Convert to a datetime object
            time_object = datetime.strptime(nmea_time_str, "%H%M%S.%f")

            # Subtract 5 hours
            new_time_object = time_object - timedelta(hours=5)

            # Format the time
            formatted_time = new_time_object.strftime("%H:%M:%S")

            #print(f"time: {formatted_time}")
            # Parse latitude
            lat_value = float(parts[2])
            #print(f"parts: {parts}")
            #print(f"Lat value: {lat_value}")
            lat_hemisphere = parts[3]
            lat_degrees = int(lat_value / 100)
            lat_minutes = lat_value - (lat_degrees * 100)
            latitude = lat_degrees + (lat_minutes / 60)
            if lat_hemisphere == 'S':
               latitude *= -1

            # Parse longitude
            lon_value = float(parts[4])
            #print(f"Long value: {lon_value}")
            lon_hemisphere = parts[5]
            lon_degrees = int(lon_value / 100)
            lon_minutes = lon_value - (lon_degrees * 100)
            longitude = lon_degrees + (lon_minutes / 60)
            if lon_hemisphere == 'W':
               longitude *= -1
            #return lat_value, lon_value, time_value
            return latitude, longitude, formatted_time
    return None, None, None


def read_gps_data(gps_lock):
    with gps_lock:
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        try: 
            start_time = time.time()
            while True:
                sentence = ser.readline().decode('utf-8', errors='ignore').strip()
                if sentence:
                    latitude, longitude, formatted_time = parse_nmea_sentence(sentence)
                    if latitude is not None and longitude is not None and formatted_time is not None:
                        return latitude, longitude, formatted_time
                # Check if timeout is reached
                if time.time() - start_time > ser.timeout:
                    print("Timeout reached. No GPS data received.")
                    break
        except KeyboardInterrupt:
            print("Program terminated!")
        finally:
            ser.close()
    return "None", "None", "None"

'''

from datetime import datetime, timedelta
import serial
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

def read_gps_data(gps_lock):
    with gps_lock:
        ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
        try: 
            start_time = time.time()
            while True:
                sentence = ser.readline().decode('utf-8', errors='ignore').strip()
                if sentence.startswith('$GNRMC'):  # Only process RMC sentences
                    latitude, longitude, formatted_time, formatted_date = parse_nmea_sentence(sentence)
                    if latitude is not None and longitude is not None and formatted_time is not None and formatted_date is not None:
                        return latitude, longitude, formatted_time, formatted_date
                # Check if timeout is reached
                if time.time() - start_time > ser.timeout:
                    print("Timeout reached. No complete GPS data received.")
                    break
        except KeyboardInterrupt:
            print("Program terminated!")
        finally:
            ser.close()
    return "None", "None", "None", "None"

    
