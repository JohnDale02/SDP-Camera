#Testcode 

import cv2

# Open a connection to the USB camera (use the appropriate camera index)
cap = cv2.VideoCapture(0)

# Check if the camera opened successfully
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    print(ret)
    # Check if the frame was read successfully
    if not ret:
        print("Error: Could not read frame.")
        break

    # 'frame' now contains the raw image data

    # You can process or save the frame as needed

    # To exit the loop, you can use a key press event (e.g., press 'q' to quit)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the OpenCV window (if any)
cap.release()
cv2.destroyAllWindows()