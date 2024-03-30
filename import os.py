import os
import cv2 as cv
import numpy as np
img = 'C:\\Users\\tejas\OneDrive\\Pictures\\Test\\IMG_0710.jpg'
img_rand_path = "C:\\Users\\tejas\\OneDrive\\Pictures\\Random\\20230603_184901.jpg"
file_name = os.path.basename(img)
print(file_name)
file_without_ext = os.path.splitext(file_name)[0]
print(file_without_ext)
img_rand = cv.imread(img_rand_path, cv.IMREAD_GRAYSCALE)
img_rand_clr = cv.imread(img_rand_path, cv.IMREAD_COLOR)
(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(img_rand)
print(maxLoc)
cv.circle(img_rand_clr, maxLoc, 10, (255, 255, 255), 10)
origin=(np.array(maxLoc)[0])
print(origin)       
img_rand.itemset(953, 1280, 0)
print(img_rand[953, 1280])
img_rand = cv.imread(img_rand_path, cv.IMREAD_GRAYSCALE)
(minVal, maxVal, minLoc, maxLoc) = cv.minMaxLoc(img_rand)
print(maxLoc)
cv.circle(img_rand, maxLoc, 10, (0, 0, 0), 10)
origin=(np.array(maxLoc)[0])
print(origin)
cv.namedWindow("img", cv.WINDOW_NORMAL)
cv.imshow('img',img_rand_clr)
cv.waitKey(0)
cv.destroyAllWindows()