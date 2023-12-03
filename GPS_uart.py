import serial
from datetime import datetime, timedelta
import time 

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
        print(f"valid: {valid}")
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

            print(f"time: {formatted_time}")
            # Parse latitude
            lat_value = float(parts[2])
            print(f"parts: {parts}")
            print(f"Lat value: {lat_value}")
            lat_hemisphere = parts[3]
            lat_degrees = int(lat_value / 100)
            lat_minutes = lat_value - (lat_degrees * 100)
            latitude = lat_degrees + (lat_minutes / 60)
            if lat_hemisphere == 'S':
               latitude *= -1

            # Parse longitude
            lon_value = float(parts[4])
            print(f"Long value: {lon_value}")
            lon_hemisphere = parts[5]
            lon_degrees = int(lon_value / 100)
            lon_minutes = lon_value - (lon_degrees * 100)
            longitude = lon_degrees + (lon_minutes / 60)
            if lon_hemisphere == 'W':
               longitude *= -1
            #return lat_value, lon_value, time_value
            return latitude, longitude, formatted_time
    return None, None, None


def read_gps_data():
    
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=5)
    try: 
        start_time = time.time()
        while True:
            sentence = ser.readline().decode('utf-8', errors='ignore').strip()
            if sentence:
                latitude, longitude, formatted_time = parse_nmea_sentence(sentence)
                if latitude is not None and longitude is not None and formatted_time is not None:
                    #print(f"Latitude: {latitude}, Longitude: {longitude}, time: {formatted_time}")
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

    

#read_gps_data()


