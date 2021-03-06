# importing OpenCV, time and Pandas library
import cv2, time, pandas, numpy as np, math, pyautogui

def main():
    # Capturing video
    video = cv2.VideoCapture(0)
    pyautogui.FAILSAFE = False #for debugging

    # Initializing coordinates
    cX_Green = 10
    cY_Green = 10
    avg_x_Green = 10
    avg_y_Green = 10
    cX_Blue = 10
    cY_Blue = 10
    avg_x_Blue = 10
    avg_y_Blue = 10

    clickDown = False

    clickTime = None
    dragging = False
    recentPointsBlue = [] #I think I'll keep the last 4 points
    recentPointsGreen = []
    #dragPnt = []

    # Initializing color boundaries
    lower_green = np.array([41, 56, 78])
    upper_green = np.array([83, 255, 255])
    lower_blue = np.array([95,50,90])
    upper_blue = np.array([133,255,255])


    # Infinite while loop to treat stack of image as video
    while True:

        # Reading frame(image) from video
        check, originalFrame = video.read()
        frame1 = cv2.GaussianBlur(originalFrame, (9, 9), 0)  # blur it

        # Apply hsv mask
        hsv_img = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)

        thresh_frame_Blue = cv2.inRange(hsv_img, lower_blue, upper_blue)
        thresh_frame_Blue = cv2.dilate(thresh_frame_Blue, None, iterations=2)

        thresh_frame_Green = cv2.inRange(hsv_img, lower_green, upper_green)
        thresh_frame_Green = cv2.dilate(thresh_frame_Green, None, iterations=2)

        height, width = thresh_frame_Blue.shape

        ret, thresh_frame_Green = cv2.threshold(thresh_frame_Green, 40, 255, 0)
        contours, hierarchy = cv2.findContours(thresh_frame_Green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            # find the biggest countour (c) by the area
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            # draw the biggest contour (c) in green
            cv2.rectangle(originalFrame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            #create mask
            mask = np.ones(thresh_frame_Green.shape[:2], dtype="uint8") * 255
            c = cv2.bitwise_not(c);
            cv2.drawContours(mask, [c], -1, 0, -1)
            thresh_frame_Green = cv2.bitwise_and(thresh_frame_Green, thresh_frame_Green, mask=mask)

        ret, thresh_frame_Blue = cv2.threshold(thresh_frame_Blue, 40, 255, 0)
        contours, hierarchy = cv2.findContours(thresh_frame_Blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if len(contours) != 0:
            # find the biggest countour (c) by the area
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            # draw the biggest contour (c) in green
            cv2.rectangle(originalFrame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # create mask
            mask = np.ones(thresh_frame_Blue.shape[:2], dtype="uint8") * 255
            c = cv2.bitwise_not(c);
            cv2.drawContours(mask, [c], -1, 0, -1)
            thresh_frame_Blue = cv2.bitwise_and(thresh_frame_Blue, thresh_frame_Blue, mask=mask)

        M = cv2.moments(thresh_frame_Green) #calculate moments of binary image
        if M["m00"] != 0:
            cX_Green = int(M["m10"] / M["m00"])
            cY_Green = int(M["m01"] / M["m00"])

        M = cv2.moments(thresh_frame_Blue)
        if M["m00"] != 0:
            cX_Blue = int(M["m10"] / M["m00"])
            cY_Blue = int(M["m01"] / M["m00"])

        #Finding the average for the last four points.
        recentPointsGreen.append([cX_Green, cY_Green])
        if len(recentPointsGreen) > 8:
            recentPointsGreen.pop(0)  # remove the last entered, like a queue
        avg_x_Green = 0
        avg_y_Green = 0
        check_x_Green = 0
        for r in range(len(recentPointsGreen)):
            avg_x_Green += recentPointsGreen[r][0]
            avg_y_Green += recentPointsGreen[r][1]
            if r > 4:
                check_x_Green += recentPointsGreen[r][0]
        avg_x_Green /= len(recentPointsGreen)
        avg_y_Green /= len(recentPointsGreen)
        avg_x_Green = int(avg_x_Green)
        avg_y_Green = int(avg_y_Green)
        check_x_Green /= 3
        check_x_Green = int(check_x_Green)

        recentPointsBlue.append([cX_Blue, cY_Blue])
        if len(recentPointsBlue) > 8:
            recentPointsBlue.pop(0)  # remove the last entered, like a queue
        avg_x_Blue = 0
        avg_y_Blue = 0
        check_x_Blue = 0
        for r in range(len(recentPointsBlue)):
            avg_x_Blue += recentPointsBlue[r][0]
            avg_y_Blue += recentPointsBlue[r][1]
            if r > 4:
                check_x_Blue += recentPointsBlue[r][0]
        avg_x_Blue /= len(recentPointsBlue)
        avg_y_Blue /= len(recentPointsBlue)
        avg_x_Blue = int(avg_x_Blue)
        avg_y_Blue = int(avg_y_Blue)
        check_x_Blue /= 3
        check_x_Blue = int(check_x_Blue)


        if not(math.fabs(avg_x_Blue-avg_x_Green) < 10 and math.fabs(avg_y_Blue-avg_y_Green) < 10): #not set to default pos.
            pyautogui.moveTo((width-avg_x_Green)*3, (avg_y_Green*2.125 + (avg_y_Green-height//2)*1.5+30), 0)

            if math.fabs(check_x_Blue-check_x_Green) < 30:
                # difference between two points. clickDown to prevent multiple clicks on one spot until raising
                if clickDown:
                    if time.time() - clickTime > 0.3:
                        if not dragging:
                            pyautogui.mouseDown()
                            dragging = True
                            #dragPnt[0] = largestCirc[0]
                            #dragPnt[1] = largestCirc[1]
                            print("Hold down. Logged drag start point.")
                else:
                    clickDown = True
                    clickTime = time.time()
            elif math.fabs(check_x_Blue-check_x_Green) > 40:
                if clickDown:  #click down was and they released.
                    if not dragging:
                        pyautogui.click((width-avg_x_Green)*3, (avg_y_Green*2.125 + (avg_y_Green-height//2)*1.5+30))
                        print("Clicked.")
                    else:
                        dragging = False
                        print("Drag released.")
                        pyautogui.mouseUp()
                        #dragPnt = []
                clickDown = False

        """TESTING
        cv2.imshow("New Image", newImage) #displaying new image drawn on
        """
        cv2.imshow("Original frame", originalFrame) #displaying original image with color circle

        key = cv2.waitKey(1)
        # stop process on q press
        if key == ord('q'):
            break

    video.release()

    # Destroying all the windows
    cv2.destroyAllWindows()


##################################################################### RUNS THE MAIN
if __name__ == "__main__":
    main()
