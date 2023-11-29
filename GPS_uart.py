import serial

def parse_gga(sentence):
    """Parse a GGA sentence to extract latitude and longitude."""
    fields = sentence.split(',')

    # Latitude
    lat_value = float(fields[2])
    lat_hemisphere = fields[3]
    lat_degrees = int(lat_value / 100)
    lat_minutes = lat_value - (lat_degrees * 100)
    latitude = lat_degrees + (lat_minutes / 60)
    if lat_hemisphere == 'S':
        latitude *= -1

    # Longitude
    lon_value = float(fields[4])
    lon_hemisphere = fields[5]
    lon_degrees = int(lon_value / 100)
    lon_minutes = lon_value - (lon_degrees * 100)
    longitude = lon_degrees + (lon_minutes / 60)
    if lon_hemisphere == 'W':
        longitude *= -1

    return latitude, longitude

# Set up the serial connection (adjust the port and baud rate according to your setup)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

try:
    while True:
        data = ser.readline().decode('ascii', errors='ignore').strip()
        if data.startswith('$GPGGA'):
            lat, lon = parse_gga(data)
            print(f"Latitude: {lat}, Longitude: {lon}")
except KeyboardInterrupt:
    print("Program terminated!")
finally:
    ser.close()
