import serial

def parse_nmea_sentence(sentence):
    """Parse GNGGA or GNRMC sentence to extract latitude and longitude."""
    parts = sentence.split(',')

    if parts[0] in ['$GNGGA', '$GNRMC']:
        # Check if the data is valid
        if parts[0] == '$GNGGA' and parts[6] != '0':
            valid = True
        elif parts[0] == '$GNRMC' and parts[2] == 'A':
            valid = True
        else:
            valid = False

        if valid:
            # Parse latitude
            lat_value = float(parts[2])
            lat_hemisphere = parts[3]
            lat_degrees = int(lat_value / 100)
            lat_minutes = lat_value - (lat_degrees * 100)
            latitude = lat_degrees + (lat_minutes / 60)
            if lat_hemisphere == 'S':
                latitude *= -1

            # Parse longitude
            lon_value = float(parts[4])
            lon_hemisphere = parts[5]
            lon_degrees = int(lon_value / 100)
            lon_minutes = lon_value - (lon_degrees * 100)
            longitude = lon_degrees + (lon_minutes / 60)
            if lon_hemisphere == 'W':
                longitude *= -1

            return latitude, longitude
    return None, None

# Set up the serial connection (adjust the port and baud rate according to your setup)
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

try:
    while True:
        sentence = ser.readline().decode('utf-8', errors='ignore').strip()
        latitude, longitude = parse_nmea_sentence(sentence)
        if latitude is not None and longitude is not None:
            print(f"Latitude: {latitude}, Longitude: {longitude}")
except KeyboardInterrupt:
    print("Program terminated!")
finally:
    ser.close()
