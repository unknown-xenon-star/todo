import cv2
vid = cv2.VideoCapture("./20251111_121843.mp4")

count, success = 0, True
while success:
    success, image = vid.read() # Read frame
    if success:
        print("|", end='')
        cv2.imwrite(f"./path_to_images/frame{count}.jpg", image) # Save frame
        count += 1

vid.release()
print("\n\tDONE\n")