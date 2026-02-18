import cv2
import numpy as np
from glob import glob

# Load images from a directory

image_files = glob("path_to_images/*.jpg")
print("Reading Files")
images = [cv2.imread(img) for img in image_files]

print("Starting Processing")
# Convert images to numpy array
image_stack = np.stack(images, axis=3)
print("Done Stage1, Starting stage 2")

# Compute median along the image stack axis
from scipy import stats

mode_image = stats.(image_stack, axis=3).astype(np.uint8)

# Save or diaply the background image
cv2.imwrite("background_no_man.jpg", mode_image)
cv2.imshow("Background", mode_image)
cv2.waitKey(0)
cv2.destroyAllWindows()