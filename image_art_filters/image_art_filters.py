import cv2
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
matplotlib.rcParams['figure.figsize'] = (10.0, 10.0)
matplotlib.rcParams['image.cmap'] = 'gray'

def createSketchFilter(image, arguments=0):
    # convert to grayscale
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blur
    img_blur = cv2.GaussianBlur(img_gray, (5,5), 3)
#     img_blur = cv2.medianBlur(img_gray, 7)
    # edge detection
    img_laplacian = cv2.Laplacian(img_blur, cv2.CV_8U, ksize=3, scale=2, delta = 2)
    # threshold edges
    retVal, img_thresholdInverse = cv2.threshold(img_laplacian, 16, 255, cv2.THRESH_BINARY_INV)
    # convert image to color as this is what is expected by the function call
    mySketchFilterImg = cv2.cvtColor(img_thresholdInverse, cv2.COLOR_GRAY2BGR)

    return mySketchFilterImg

def createCartoonFilter(image, arguments=0):
    
    # Blur image whilst preserving the edges
    img_blur = cv2.edgePreservingFilter(image, flags=1, sigma_s=150, sigma_r=0.4)
    # Get the contours of the image from the function we already made
    img_contours = createSketchFilter(image)
    img_contours_gray = cv2.cvtColor(img_contours, cv2.COLOR_BGR2GRAY)
    # Return the masked image (as explained on stack overflow)
    myCartoonFilterImg =  cv2.bitwise_and(img_blur, img_blur, mask = img_contours_gray)
    
    return myCartoonFilterImg
    
    
imagePath = r"example_image/Kamala_Harris.jpg"
# imagePath = r"example_image/Barack_Obama.jpg"
image = cv2.imread(imagePath)

sketchFilterImg = createSketchFilter(image)
cartoonFilterImg = createCartoonFilter(image)

plt.figure(figsize=[20,10])
plt.subplot(131);plt.imshow(image[:,:,::-1]);
plt.subplot(132);plt.imshow(sketchFilterImg[:,:,::-1]);
plt.subplot(133);plt.imshow(cartoonFilterImg[:,:,::-1]);
plt.show()
