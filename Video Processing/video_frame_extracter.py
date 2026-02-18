import cv2
import os

video_list = [i for i in os.listdir() if i.endswith((".mp4",".mkv"))]

if len(video_list) == 1:
    video_path = video_list[0]
elif len(video_list) > 1:
    text = [f"{idx}. {file}" for idx, file in enumerate(video_list, 1)]
    print("Choose FILE No: \n"+"\n".join(text))
    video_no = int(input("\nENTER FILE NO: "))
    if not (video_no>0 and video_no<=len(video_list)):
        raise ValueError("INVALID video NO")
    video_path = video_list[video_no]
else:
    raise FileExistsError("No Video file('mkv', 'mp4') FOund")
# video_path = "./movie.mp4"
print("VIDEO_PATH:", video_path)
output_path = "./path_to_images"

os.makedirs(output_path, exist_ok=True)

vid = cv2.VideoCapture(video_path)

if not vid.isOpened():
    print("Error opening video file")
    exit()

count = 0

while True:
    success, frame = vid.read()
    if not success:
        break
    
    cv2.imwrite(f"{output_path}/frame{count:05d}.jpg", frame)
    print("|", end="")
    count += 1

vid.release()
print("\nDONE")