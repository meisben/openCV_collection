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

global exitStateMachine
exitStateMachine = False

# playVideo = True
# colorSelected = False
# videoReadyToStart = False
# videoStarted = False

# ------------------------------------------#
# Functions (global)                        #
# ------------------------------------------#

def readGlobalVideoFrame():
    global currentVideo
    global currentFrame
    ret, currentFrame = currentVideo.read()


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
#  States for the State Machine             #
# ------------------------------------------#

def loadForegroundVideo():
    """
    Purpose: to load the background video
    Notes: N/A
    """
    global programState
    global currentVideo
    global currentVideoLength

    currentVideo = cv2.VideoCapture(foregroundVideoPath)
    if (currentVideo.isOpened()== False):
        raise Exception("Error opening video file with path {}".format(foregroundVideoPath))
    frame_count_property_id = int(cv2.CAP_PROP_FRAME_COUNT)
    currentVideoLength = int(cv2.VideoCapture.get(currentVideo, frame_count_property_id))

    # Print info on the loaded video file
    print("property_id: {}, capLength: {}".format(frame_count_property_id, currentVideoLength))

    # Read first frame
    readGlobalVideoFrame()

    # Transition to next state
    programState = 1


def backgroundColorSelection():
    """
    Purpose: to load the foreground video
    Notes: to allow user to select background color to be removed from foreground video
    """
    global programState
    global currentFrame
    global clickBackgroundColor

    # ---Inner Function-------------------------#

    def mouseClickCallback(mouseAction, xPocs, yPos, flags, myImg):
        """ Inner Function determines action when cuser clicks on background color
        """
        global clickBackgroundColor
        # print(mouseAction)
        if mouseAction == cv2.EVENT_LBUTTONDOWN or mouseAction == cv2.EVENT_RBUTTONDOWN:
            clickBackgroundColor = True

    # --- Main body of Function----------------#

    cv2.namedWindow(imageWindowName)
    cv2.setMouseCallback(imageWindowName, mouseClickCallback, currentFrame)
    clickBackgroundColor = False

    k = 0
    while clickBackgroundColor != True:
        cv2.imshow(imageWindowName, currentFrame)
        k = cv2.waitKey(20)

    if clickBackgroundColor == True:
        # Color section is completed
        cv2.destroyAllWindows()
        programState = 2

def prepareVideoToPlay():
    """
    Purpose: to start the foreground video playing in a named window
    Notes: 
    """
    global programState
    global currentFrame

    cv2.namedWindow(videoWindowName, cv2.WINDOW_AUTOSIZE)
    cv2.imshow(videoWindowName, currentFrame) #display the first frame

    # Create trackbars
    # cv2.createTrackbar("Progress", videoWindowName, 0 , 100, progressTrackbarCallback)
    # cv2.createTrackbar("Tolerance", videoWindowName, toleranceFactor, 100, lambda *args: onChangeTolerance())
    # cv2.createTrackbar("Softness", videoWindowName, softnessFactor, 100, lambda *args: onChangeSoftness())
    # cv2.createTrackbar("Defringe", videoWindowName, defringeFactor, 100, lambda *args: onChangeDefringe())

    programState = 3

def videoPlaying():
    """
    Purpose: to define activity whilst playing
    Notes: 
    """
    global programState
    global currentFrame

    # Read new frame
    readGlobalVideoFrame()

    # Display the resulting frame
    cv2.imshow(videoWindowName, currentFrame)

    key = cv2.waitKey(20)

    if key & 0xFF == 27:
        cv2.destroyAllWindows()
        programState = 5
    

def videoPaused():
    """
    Purpose: to pause the video
    Notes: 
    """
    global programState

    programState = 5

def exitStateMachine():
    global programState
    global exitStateMachine
    exitStateMachine = True
    


#---------------------
# Our State Machine
#--------------------- 

# The state is passed to the switcher object
switcher = {
    0: loadForegroundVideo,
    1: backgroundColorSelection,
    2: prepareVideoToPlay,
    3: videoPlaying,
    4: videoPaused,
    5: exitStateMachine
  }

# Create our state machine
def ourStateMachine(programState):

  # Defines error message if incorrect state is requested
  func = switcher.get(programState, "Invalid State") 
  func()


# ------------------------------------------#
# Main Program                              #
# ------------------------------------------#

# Key parameters
foregroundVideoPath = r"example_video\foreground\greenscreen-asteroid.mp4"
programState = 0 # sets state machine starting state

# Print ready message
print("Program is running, follow instructions on screen")

while True:
    ourStateMachine(programState)
    if exitStateMachine == True:
        break
    # print("robotState = {}").format(programState)







# i = 0
# while(capFore.isOpened()):
    
#     # This acts as a state machine, you can see this by uncommenting this line
#     if i%10 = 0:
#         print("Cycle: {}".format(i))

#     # Capture frame-by-frame
#     if playVideo:
#         ret, frame = capFore.read()
#         if ret == True:
#             resultFrame = frame

#     if colorSelected = False:
#         # allow the user to select a background color
#         userSelectBackgroundColor(frame)

#     if videoReadyToStart = True:
#         # Create a video window to display the results of the green screen removal
#         cv2.namedWindow(videoWindowName, cv2.WINDOW_AUTOSIZE)

#     key = cv2.waitKey(25)
#     # if esc is pressed
#     if key & 0xFF == 27:
#         break
#     # if spacebar is pressed
#     if key & 0xFF == 32:
#         playVideo = not playVideo

#     # Display the resulting frame
#     cv2.imshow(videoWindowName, frame)

#     # display progress trackbar
#     capForeFrameNumber = capFore.get(cv2.CAP_PROP_POS_FRAMES); 
#     cv2.createTrackbar("Progress", videoWindowName, int(capForeFrameNumber / capForeLength * 100) , 100, progressTrackbarCallback)

#     # other trackbars
#     # cv2.createTrackbar("Tolerance", videoWindowName, toleranceFactor, 100, lambda *args: onChangeTolerance())
#     # cv2.createTrackbar("Softness", videoWindowName, softnessFactor, 100, lambda *args: onChangeSoftness())
#     # cv2.createTrackbar("Defringe", videoWindowName, defringeFactor, 100, lambda *args: onChangeDefringe())

# cv2.destroyAllWindows()