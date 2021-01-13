# imports
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def debugShowImage(myImage):
    # myImage = cv2.cvtColor(myImage, cv2.COLOR_GRAY2BGR)
    print(myImage.shape)
    plt.figure(figsize=[5,5])
    plt.imshow(myImage[:,:,::-1])
    plt.show()

def mouseClickCallback(mouseAction, xPos, yPos, flags, myImg):
    """
    Function description
    """
    if mouseAction == cv2.EVENT_LBUTTONDOWN or mouseAction == cv2.EVENT_RBUTTONDOWN:
        replacementPatch = findBestMatchingPatch(xPos,yPos, patchLength = 30, borderSize = 30, myImg = myImg)
        # debugShowImage(replacementPatch)

        # seamless clone the patch onto the image
        src_mask = np.ones_like(replacementPatch) * 255
        cv2.seamlessClone(
            replacementPatch, img, src_mask, (xPos, yPos), cv2.NORMAL_CLONE, blend=img)

def findBestMatchingPatch(xPos,yPos,patchLength,borderSize,myImg):
    print("Image Shape = ", myImg.shape)
    bestVariance = 0
    bestDistFromTargetMean = 999 # a large number
    bestXPos = None
    bestYPos = None
    thresholdVariance = 380 # from experimentation
    print("Initial X, Y = ", yPos, xPos)
    selectedPatch = getPatch(xPos,yPos,patchLength, myImg)
    selectedPatch_mean = selectedPatch.mean()
    print("SelectedPatch_mean = ", selectedPatch_mean)
    movementsArray = np.array([(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]) * patchLength
    for movement in movementsArray:
        newXPos = xPos + movement[0]
        newYPos = yPos + movement[1]
        # print("Mod X, Y = ", newXPos, newYPos)
        
        candidatePatch = getPatch(newXPos,newYPos,patchLength, myImg) 
        # debugShowImage(patch)
        patchVariance = calcImgVariance(candidatePatch)
        patchMean = calcBorderImgMean(candidatePatch,borderSize)
        distFromTargetMean = abs(selectedPatch_mean - patchMean)
        print("patchVariance = ", patchVariance)
        print("patchMean = ", patchVariance)
        # Use inverse of variance to calculate the highest
        if patchVariance < thresholdVariance and distFromTargetMean < bestDistFromTargetMean:
            bestDistFromTargetMean = distFromTargetMean
            bestVariance = patchVariance
            bestXPos = newXPos
            bestYPos = newYPos

    if(bestXPos == None):
        raise Exception("error: Sorry, candidate patch not found under defined threshold variance of {}, please increase the variance".format(thresholdVariance))

    print("replacementPatch info = x:{}, y:{}, variance:{}, distFromMean: {}".format(bestXPos, bestYPos, bestVariance, bestDistFromTargetMean))
    
    return getPatch(bestXPos,bestYPos,patchLength, myImg) 

def getPatch(myXPos,myYPos, patchLength, myImg):
    y1 = int(round((myYPos - patchLength/2), ndigits= None))
    y2 = int(round((myYPos + patchLength/2), ndigits= None))
    x1 = int(round((myXPos - patchLength/2), ndigits= None))
    x2 = int(round((myXPos + patchLength/2), ndigits= None))
    print("Patch dims: y1: {}, y2: {}, x1: {}, x2: {}".format(y1,y2,x1,x2))
    patch = img[y1:y2, x1:x2]
    return patch


def calcImgVariance(myPatch):
    grayPatch = cv2.cvtColor(myPatch, cv2.COLOR_BGR2GRAY)
    return cv2.Laplacian(grayPatch, cv2.CV_64F).var()


def calcBorderImgMean(mySelectedPatch, borderSize):
    mySelectedPatch_gray = cv2.cvtColor(mySelectedPatch, cv2.COLOR_BGR2GRAY)
    ySize,xSize = mySelectedPatch_gray.shape

    # find the borders
    borderUpper = mySelectedPatch_gray[0:borderSize, 0:xSize]
    borderLower = mySelectedPatch_gray[ySize-borderSize:ySize, 0:xSize]
    borderLeft = mySelectedPatch_gray[0:ySize, 0:borderSize]
    borderRight = mySelectedPatch_gray[0:ySize, xSize-borderSize:xSize]

    #find overall mean
    overallMean = (borderUpper.mean() + borderLower.mean() + borderLeft.mean() + borderRight.mean()) / 4
    
    return overallMean

# Read the image
imgPath = r"example_image/example_img2.jpg"
img = cv2.imread(imgPath, 1)
print(img.shape)
# Create named window
cv2.namedWindow("Window")
# Callback events enabled for the window (img passed as fith parameter)
cv2.setMouseCallback("Window", mouseClickCallback, img)

k = 0
while k != 27:
    cv2.imshow("Window", img)
    k = cv2.waitKey(20)

cv2.destroyAllWindows()

