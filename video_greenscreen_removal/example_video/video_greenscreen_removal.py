# ------------------------------------------#
# Imports                                   #
# ------------------------------------------#

import cv2
import numpy as np

# ------------------------------------------#
# Global Variables                          #
# ------------------------------------------#

imageWindowName = "Background color selector"
videoWindowName = "Greenscreen Video"

clickBackgroundColor = False

# ------------------------------------------#
# Functions (background color selection)    #
# ------------------------------------------#

def userSelectBackgroundColor(myImg):
    """ Function allows user to select background color to be removed from video
    """
    global clickBackgroundColor
    clickBackgroundColor = False

    cv2.namedWindow(imageWindowName)
    cv2.setMouseCallback(imageWindowName, mouseClickCallback, myImg)

    k = 0
    while k != 27 and clickBackgroundColor == True:
        cv2.imshow(imageWindowName, myImg)
        k = cv2.waitKey(20)

def mouseClickCallback(mouseAction, xPos, yPos, flags, myImg):
    """ Function determines action when user clicks on background color
    """
    print(mouseAction)
    if mouseAction == cv2.EVENT_LBUTTONDOWN or mouseAction == cv2.EVENT_RBUTTONDOWN:
        clickBackgroundColor = True
        print("Mouse clicked")

# ------------------------------------------#
# Functions (Chroma Keying)                 #
# ------------------------------------------#

def performChromaKeying(myFrame):
    """ Function executes on each video frame to perform green screen removal
    """
    


def progressTrackbarCallback(*args):
    """ Function executes each time position is slected on progress trackbar
    """
    print("Progress Trackbar moved to position:")
    print(*args)
    pass


# ------------------------------------------#
# Main Program                              #
# ------------------------------------------#

# load the foreground video file
foregroundVideoPath = r"example_video\foreground\greenscreen-asteroid.mp4"

capFore = cv2.VideoCapture(foregroundVideoPath)
if (capFore.isOpened()== False): 
    raise Exception("Error opening video file with path {}".format(foregroundVideoPath))
frame_count_property_id = int(cv2.CAP_PROP_FRAME_COUNT)
capForeLength = int(cv2.VideoCapture.get(capFore, frame_count_property_id))

# Print info on the loaded video file
print("property_id: {}, capLength: {}".format(frame_count_property_id, capForeLength))

playVideo = True
firstPlayOfVideo = True

while(capFore.isOpened()):
    print("hello")
    # Capture frame-by-frame
    if playVideo:
        ret, frame = capFore.read()
        if ret == True:
            resultFrame = frame

    if firstPlayOfVideo:
        # allow the user to select a background color
        userSelectBackgroundColor(frame)
        # Create a video window to display the results of the green screen removal
        cv2.namedWindow(videoWindowName, cv2.WINDOW_AUTOSIZE)
        firstPlayOfVideo = not firstPlayOfVideo

    key = cv2.waitKey(25)
    # if esc is pressed
    if key & 0xFF == 27:
        break
    # if spacebar is pressed
    if key & 0xFF == 32:
        playVideo = not playVideo

    # Display the resulting frame
    cv2.imshow(videoWindowName, frame)

    # display progress trackbar
    capForeFrameNumber = capFore.get(cv2.CAP_PROP_POS_FRAMES); 
    cv2.createTrackbar("Progress", videoWindowName, int(capForeFrameNumber / capForeLength * 100) , 100, progressTrackbarCallback)

    # other trackbars
    # cv2.createTrackbar("Tolerance", videoWindowName, toleranceFactor, 100, lambda *args: onChangeTolerance())
    # cv2.createTrackbar("Softness", videoWindowName, softnessFactor, 100, lambda *args: onChangeSoftness())
    # cv2.createTrackbar("Defringe", videoWindowName, defringeFactor, 100, lambda *args: onChangeDefringe())

cv2.destroyAllWindows()