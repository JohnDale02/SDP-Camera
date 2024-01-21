from PIL import Image, ImageDraw
import os
import random
import json

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def modify_image(file_path):
    with Image.open(file_path) as img:
        draw = ImageDraw.Draw(img)

        # Draw some random lines
        for _ in range(5):  # Drawing 5 random lines
            start_point = (random.randint(0, img.width), random.randint(0, img.height))
            end_point = (random.randint(0, img.width), random.randint(0, img.height))
            draw.line([start_point, end_point], fill=random_color(), width=3)

        # Save the modified image

        new_file_path = file_path
        img.save(new_file_path)

def modify_json(json_filepath):
    # Read the JSON data
    with open(json_filepath, 'r') as file:
        data = json.load(file)

        key = random.choice(list(data.keys()))
        while key == 'Camera Number' or key == 'Signature_Base64':
            key = random.choice(list(data.keys()))


        if isinstance(data[key], str):
            data[key] += 'x'         # Append 'x' to a string

    # Write the modified data back to a file

    with open(json_filepath, 'w') as file:
        json.dump(data, file)

    print(f"Modified JSON saved to {json_filepath}")


count = 0
for i in range(41):
    if count % 2 == 0: # number is even
        modify_image(f'TestImages/{i}.png')

    else:  # number is odd
        modify_json(f'TestImages/{i}.json')

    count += 1
    
