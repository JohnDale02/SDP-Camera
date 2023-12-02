from main import main 
import os 
import time 

camera_number_string = "1"  # camera number used to search for public key
if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

start_time = time.time()
for i in range(40): 
  main(camera_number_string, save_image_filepath)
end_time = time.time()
Total_time = end_time - start_time
print(Total_time)