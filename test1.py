import os
import cv2 as cv
import numpy as np

img_path = "C:\\Users\\tejas\OneDrive\\Pictures\\Test\\IMG_0710.jpg"

img = cv.imread(img_path)
img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img = cv.GaussianBlur(img, (5, 5), 0)


img_array = np.array(img)
bulb = np.unravel_index(img_array.argmax(), img_array.shape)
print(img_array.max(), bulb)
print(img_array[bulb])
bulb_new = np.where(img_array == img_array.min())
print(bulb_new[0][0])
img_array[bulb] = 255
img_array[bulb[0], bulb[1]] = 0
cv.circle(img_array, (bulb_new[1][0],bulb_new[0][0]), 100, 255, 100)

#img = cv.imread(img_path, cv.IMREAD_GRAYSCALE)

print(img_array.min(), np.unravel_index(img_array.argmin(), img_array.shape))
bulb = np.unravel_index(img_array.argmin(), img_array.shape)
print(bulb)
cv.circle(img_array, (bulb[1],bulb[0]), 20, 0, 20)
print(img_array[bulb])

cv.namedWindow("img", cv.WINDOW_NORMAL)
cv.imshow('img',img_array)
cv.waitKey(0)
cv.destroyAllWindows()
