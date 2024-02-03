import cv2

def encode_video_to_bytes(video_path: str) -> bytes:
    # Read video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return b''

    # Initialize byte array
    video_bytes = bytearray()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Encode frame
        _, encoded_frame = cv2.imencode('.jpg', frame)
        video_bytes.extend(encoded_frame.tobytes())

    cap.release()
    return bytes(video_bytes)

def create_combined_vid(camera_number: str, video_path: str, time: str, location: str) -> bytes:
    '''Takes in camera number, video path, time, location and combines them into one byte object'''
    
    encoded_video = encode_video_to_bytes(video_path)  # This will be quite large for videos

    encoded_number = camera_number.encode('utf-8')
    encoded_time = time.encode('utf-8')
    encoded_location = location.encode('utf-8')

    combined_data = encoded_number + encoded_video + encoded_time + encoded_location

    return combined_data
