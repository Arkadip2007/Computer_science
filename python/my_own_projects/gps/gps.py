import serial

port = "/dev/ttyUSB0"   # তোমার port
baud = 9600

ser = serial.Serial(port, baud, timeout=1)

def convert_to_decimal(coord, direction):
    deg = int(coord[:2])
    minutes = float(coord[2:])
    decimal = deg + (minutes / 60)

    if direction in ['S', 'W']:
        decimal = -decimal

    return decimal


print("Reading GPS data...\n")

satellites = "0"

while True:
    line = ser.readline().decode(errors="ignore").strip()

    # Satellite data
    if line.startswith("$GPGGA"):
        data = line.split(",")
        if len(data) > 7:
            satellites = data[7]

    # Location data
    if line.startswith("$GPRMC"):
        data = line.split(",")

        if data[2] == "A":  # valid fix
            time = data[1]
            lat = data[3]
            lat_dir = data[4]
            lon = data[5]
            lon_dir = data[6]
            speed = data[7]

            latitude = convert_to_decimal(lat, lat_dir)
            longitude = convert_to_decimal(lon, lon_dir)

            print("====== GPS DATA ======")
            print("Time (UTC):", time)
            print("Latitude :", latitude)
            print("Longitude:", longitude)
            print("Satellites:", satellites)
            print("Speed (knots):", speed)
            print("Map:", f"https://maps.google.com/?q={latitude},{longitude}")
            print("----------------------\n")
