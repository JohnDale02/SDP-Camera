from main import main 
import os 
import time 

camera_number_string = "1"  # camera number used to search for public key
if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

start_time = time.time()

#while button not pressed and files in path and wifi - upload images 


for i in range(10): 
  main(camera_number_string, save_image_filepath)

time.sleep(10)


while True: 
  if (button_press):
    main(camera_number_string, save_image_filepath)
  elif(check_wifi() && (there exists files in save_image_filepath)):
        upload_saved_image() #only one image 
        if os.listdir(directory_path):
          print("Directory is not empty.")
        else:
          print("Directory is empty.")

end_time = time.time()
Total_time = end_time - start_time
print(Total_time)