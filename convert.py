import subprocess

def convert_video(input_file, output_file):
    command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        output_file
    ]
    
    # Execute the command
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check if the conversion was successful
    if process.returncode == 0:
        print("Conversion successful.")
    else:
        print("Conversion failed.")
        # Output the error
        print(process.stderr.decode())

# Example usage
input_mkv = 'output.mkv'
output_mp4 = 'ZoutpuT.mp4'
convert_video(input_mkv, output_mp4)
