import base64
import mysql.connector
import os


def get_public_key(camera_number):
    # Environment variables for database connection
    #host = os.environ['DB_HOST']
    #user = os.environ['DB_USER']
    #password = os.environ['DB_PASSWORD']
    #database = os.environ['DB_NAME']
    host = "publickeycamerastorage.c90gvpt3ri4q.us-east-2.rds.amazonaws.com"
    user = "sdp"
    password = "sdpsdpsdp"
    database = "PublicKeySchema"

    # Connect to the database
    connection = mysql.connector.connect(
        host=host, user=user, password=password, database=database
    )
    cursor = connection.cursor()

    # SQL query to retrieve the public key
    query = "SELECT PublicKey FROM Cameras WHERE CameraNumber = %s"

    cursor.execute(query, (int(camera_number),))

    # Fetch the result
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        public_key = result[0]
    
        return public_key  # Return the public key
    
    else:
        return 'Public key not found'
