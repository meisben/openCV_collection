# ------------------------------------------#
# Imports                                   #
# ------------------------------------------#

import cv2
import numpy as np

# ------------------------------------------#
# Global Variables                          #
# ------------------------------------------#

# foregroundVideoPath = r"example_video\foreground\greenscreen-asteroid.mp4"
foregroundVideoPath = r"example_video\foreground\greenscreen-demo.mp4"

imageWindowName = "Background color selector"
videoWindowName = "Greenscreen Video"


# global exitStateMachine
exitStateMachine = False

tolleranceChromaKeying = 50
softnessChromaKeying = 50

# ------------------------------------------#
# Functions (global)                        #
# ------------------------------------------#

def readGlobalVideoFrame():
    global capForeground
    global currentForegroundFrame
    ret, currentForegroundFrame = capForeground.read()


# ------------------------------------------#
# Functions (Chroma Keying)                 #
# ------------------------------------------#

def performChromaKeying(myFrame):
    """ Function executes on each video frame to perform green screen removal
    """
    global backgroundColorHSV # 3 element list of HSV values for selected background color
    global tolleranceChromaKeying # tollerance variable set by video track bar (user input)
    global softnessChromaKeying # softness factor set by video track bar (user input)
    
    # convert video frame from BGR to HSV color space
    frameHSV = cv2.cvtColor(myFrame,cv2.COLOR_BGR2HSV)

    # user selected background color
    hue = backgroundColorHSV[0]
    sat = backgroundColorHSV[1]
    val = backgroundColorHSV[2]

    # convert tollerance to a fraction
    fractionalTollerance = tolleranceChromaKeying / 100 # 0 to 1
    tolRng = 20 * fractionalTollerance

    # create a mask based on the user selected background color
    # print("Hue Value: ", hue)
    lower_range = np.array([hue-tolRng,120,70])
    upper_range = np.array([hue+tolRng,255,255])
    myMask = cv2.inRange(frameHSV, lower_range, upper_range)

    # open and dilate the mask to fill in any holes
    myMask = cv2.morphologyEx(myMask, cv2.MORPH_OPEN, np.ones((3,3),np.uint8))
    myMask = cv2.morphologyEx(myMask, cv2.MORPH_DILATE, np.ones((3,3),np.uint8))

    # creating an inverted mask to segment out the background from the image
    myMask = cv2.bitwise_not(myMask)

    #Segmenting the cloth out of the frame using bitwise and with the mask
    result = cv2.bitwise_and(myFrame,myFrame,mask=myMask)

    return result



def progressTrackbarCallback(*args):
    """ Function executes each time position is slected on progress trackbar
    """
    print("Progress Trackbar moved to position:")
    print(*args)
    pass

# ------------------------------------------#
# Trackbar callbacks                        #
# ------------------------------------------#

def onProgressTrackbarChange(*args):
    global capForeground, capForegroundLength
    CapForegroundProgress = cv2.getTrackbarPos("Progress", videoWindowName)
    CapForegroundProgress = int((CapForegroundProgress /100) * capForegroundLength)
    # print("Video progress (frame): ", CapForegroundProgress)
    capForeground.set(cv2.CAP_PROP_POS_FRAMES, CapForegroundProgress)
    # Read first frame of new position
    readGlobalVideoFrame()

def onToleranceTrackbarChange(*args):
    global tolleranceChromaKeying
    tolleranceChromaKeying = cv2.getTrackbarPos("Tolerance", videoWindowName)
    print("tollerance: ", tolleranceChromaKeying)


def onSoftnessTrackbarChange(*args):
    global softnessChromaKeying
    softnessChromaKeying = cv2.getTrackbarPos("Softness", videoWindowName) 

# ------------------------------------------#
#  States for the State Machine             #
# ------------------------------------------#

def loadForegroundVideo():
    """
    Purpose: to load the background video
    Notes: N/A
    """
    global programState
    global capForeground
    global capForegroundLength

    capForeground = cv2.VideoCapture(foregroundVideoPath)
    if (capForeground.isOpened()== False):
        raise Exception("Error opening video file with path {}".format(foregroundVideoPath))
    frame_count_property_id = int(cv2.CAP_PROP_FRAME_COUNT)
    capForegroundLength = int(cv2.VideoCapture.get(capForeground, frame_count_property_id))

    # Print info on the loaded video file
    print("property_id: {}, capLength: {}".format(frame_count_property_id, capForegroundLength))

    # Read first frame
    readGlobalVideoFrame()

    # Transition to next state
    programState = 1


def backgroundColorSelection():
    """
    Purpose: to load the foreground video
    Notes: to allow user to select background color to be removed from foreground video
    """
    global programState # for the state machine
    global currentForegroundFrame # frame operation is performed on
    global clickBackgroundColor # boolean to show if click event has taken place
    global backgroundColorHSV # 3 element list of HSV values for selected background color

    # ---Inner Function-------------------------#

    def mouseClickCallback(mouseAction, xPos, yPos, flags, myImg):
        """ Inner Function determines action when cuser clicks on background color
        """
        global clickBackgroundColor
        global colorSelectonCoordXY

        if mouseAction == cv2.EVENT_LBUTTONDOWN or mouseAction == cv2.EVENT_RBUTTONDOWN:
            clickBackgroundColor = True
            colorSelectonCoordXY = (xPos, yPos)

    # --- Main body of Function----------------#

    duplicateFrame = currentForegroundFrame.copy()
    cv2.putText(duplicateFrame, 'Please select background color with cursor', (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)

    frameHSV = cv2.cvtColor(currentForegroundFrame,cv2.COLOR_BGR2HSV)
    # print("HSV image shape = {}".format(frameHSV.shape))    

    cv2.namedWindow(imageWindowName)
    cv2.setMouseCallback(imageWindowName, mouseClickCallback, duplicateFrame)
    clickBackgroundColor = False

    while clickBackgroundColor != True:
        cv2.imshow(imageWindowName, duplicateFrame)
        key = cv2.waitKey(20) # variable not used
        if key & 0xFF == 27:
            # Exit program if Esc key is pressed
            print("Program exiting")
            programState = 5
            break

    if clickBackgroundColor == True:
        # Color section is completed
        print("Background color selected as (X,Y): {}".format(colorSelectonCoordXY))
        [backgroundHue, backgroundSat, backgroundVal] = frameHSV[colorSelectonCoordXY[1],colorSelectonCoordXY[0],:]
        backgroundColorHSV = [backgroundHue, backgroundSat, backgroundVal]
        print("HSV values at this position: {}, {}, {}".format(backgroundHue, backgroundSat, backgroundVal))
        cv2.destroyAllWindows()
        programState = 2

def prepareVideoToPlay():
    """
    Purpose: to start the foreground video playing in a named window, then to change state
    Notes: 
    """
    global programState
    global currentForegroundFrame

    # load window
    cv2.namedWindow(videoWindowName, cv2.WINDOW_AUTOSIZE)

    # set next program state for state machine
    programState = 3

def videoPlaying():
    """
    Purpose: to define activity whilst playing
    Notes: 
    """
    global programState
    global currentForegroundFrame
    global capForegroundLength
    global softnessChromaKeying, tolleranceChromaKeying

    # Process the frame using chroma keying (greenscreen removal)
    chromaKeyedFrame = performChromaKeying(currentForegroundFrame)
    
    # Get foreground video progress
    capForeFrameNo =  capForeground.get(cv2.CAP_PROP_POS_FRAMES)
    progressPercent = int(capForeFrameNo/capForegroundLength*100)

    # Display the resulting frame
    cv2.imshow(videoWindowName, chromaKeyedFrame)

    # Display trackbars
    cv2.createTrackbar("Progress", videoWindowName, progressPercent, 100, onProgressTrackbarChange)
    cv2.createTrackbar("Tolerance", videoWindowName, tolleranceChromaKeying, 100, onToleranceTrackbarChange)
    cv2.createTrackbar("Softness", videoWindowName, softnessChromaKeying, 100, onSoftnessTrackbarChange)

    # Wait for user input (if any)
    key = cv2.waitKey(20)

    # Read new video frame
    readGlobalVideoFrame()

    if key & 0xFF == 27 or capForeground.isOpened() == False:
        cv2.destroyAllWindows()
        # set next program state for state machine
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
    cv2.destroyAllWindows()
    print("Program closing")
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
programState = 0 # sets state machine starting state

# Print ready message
print("Program is running, follow instructions on screen")

while True:
    ourStateMachine(programState)
    if exitStateMachine == True:
        break
    # print("robotState = {}").format(programState)




