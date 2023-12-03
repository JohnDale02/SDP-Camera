from main import main 
import os 
import time 
from checkButtonPress import checkButtonPressed



camera_number_string = "1"  # camera number used to search for public key
if not os.path.exists(os.path.join(os.getcwd(), "tmpImages")): # make a directory for tmpImages if it doesnt exist
    os.makedirs(os.path.join(os.getcwd(), "tmpImages"))
save_image_filepath = os.path.join(os.getcwd(), "tmpImages")

#Test3
# start_time = time.time()
# for i in range(10): 
#   main(camera_number_string, save_image_filepath)

# end_time = time.time()
# Total_time = end_time - start_time
# print(Total_time)
# time.sleep(10)


while True: 
  if(checkButtonPressed):
    main(camera_number_string, save_image_filepath)
  
  
  
  # elif(check_wifi() && (there exists files in save_image_filepath)):
  #       upload_saved_image() #only one image 
  #       if os.listdir(directory_path):
  #         print("Directory is not empty.")
  #       else:
  #         print("Directory is empty.")
