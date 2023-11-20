import cv2
import numpy as np

# Read the images
try:
    image1 = cv2.imread('TempNewImage.png')
except Exception as e:
    print(e)

try:
    image2 = cv2.imread('NewImage.png')
except Exception as e:
    print(e)



# Check if the shapes of the images are the same
if image1.shape == image2.shape:
    # Check if the images are exactly the same
    difference = cv2.subtract(image1, image2)
    b, g, r = cv2.split(difference)

    # If all pixels are black, then the two images are the same
    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
        print("The images are completely Equal")
    else:
        print("The images are NOT equal")
else:
    print("The images have different sizes/shapes and are NOT equal")
