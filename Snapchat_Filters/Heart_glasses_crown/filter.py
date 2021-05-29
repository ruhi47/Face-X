import dlib
import cv2
from scipy.spatial import distance as dist
import numpy as np


def filter(frame, landmarks):
    """
    Placing the glass and heart crown filter on the frame.
    """
    # Storing image with the desired filter
    Glass_img = cv2.imread("glasses.png", -1)
    Crown_img = cv2.imread("crown.png", -1)

    # selecting all 3 color channels in the frame
    frame_mask_crown = Crown_img[:, :, 3]
    # Obtaining inverse mask
    frame_mask_inv_crown = cv2.bitwise_not(frame_mask_crown)
    Crown_img = Crown_img[:, :, 0:3]

    # Dimensions of actual crown
    ogCrownHt, ogCrownWd  = Crown_img.shape[:2]

    # Adjusting the height and width of crown according to landmarks
    CrownWd = abs(landmarks.part(17).x - landmarks.part(26).x) + 50
    CrownHt = int(CrownWd * ogCrownHt / ogCrownWd)
    crown = cv2.resize(Crown_img, (CrownWd, CrownHt), interpolation=cv2.INTER_AREA)
    mask = cv2.resize(frame_mask_crown, (CrownWd, CrownHt), interpolation=cv2.INTER_AREA)
    mask_inv = cv2.resize(frame_mask_inv_crown, (CrownWd, CrownHt), interpolation=cv2.INTER_AREA)

    # Obtaining the region-of-interest
    y1 = int(landmarks.part(24).y - 90)
    y2 = int(y1 + CrownHt)
    x1 = int(landmarks.part(27).x - (CrownWd / 2))
    x2 = int(x1 + CrownWd)
    roi1 = frame[y1:y2, x1:x2]
    roi_bg = cv2.bitwise_and(roi1, roi1, mask=mask_inv)
    roi_fg = cv2.bitwise_and(crown, crown, mask=mask)

    # Adding filter to the frame
    frame[y1:y2, x1:x2] = cv2.add(roi_bg, roi_fg)

    # Repeating similar procedure for the placement of the glasses
    frame_mask_glass = Glass_img[:, :, 3]

    frame_mask_inv_glass = cv2.bitwise_not(frame_mask_glass)
    Glass_img = Glass_img[:, :, 0:3]

    ogGlassHt, ogGlassWd = Glass_img.shape[:2]

    glassWd = abs(landmarks.part(16).x - landmarks.part(1).x)
    glassHt = int(glassWd * ogGlassHt / ogGlassWd)
    glass = cv2.resize(Glass_img, (glassWd, glassHt), interpolation=cv2.INTER_AREA)
    mask = cv2.resize(frame_mask_glass, (glassWd, glassHt), interpolation=cv2.INTER_AREA)
    mask_inv = cv2.resize(frame_mask_inv_glass, (glassWd, glassHt), interpolation=cv2.INTER_AREA)

    y1 = int(landmarks.part(24).y)
    y2 = int(y1 + glassHt)
    x1 = int(landmarks.part(27).x - (glassWd / 2))
    x2 = int(x1 + glassWd)
    roi1 = frame[y1:y2, x1:x2]
    roi_bg = cv2.bitwise_and(roi1, roi1, mask=mask_inv)
    roi_fg = cv2.bitwise_and(glass, glass, mask=mask)

    frame[y1:y2, x1:x2] = cv2.add(roi_bg, roi_fg)

    return frame


def main():
    """
    Here we detect face and the landmarks through a live video feed.
    We use these facial landmarks to place the filter accordingly.
    """

    # detecting the face in the feed
    detector = dlib.get_frontal_face_detector()
    # locating the facial landmarks
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

    # Getting video feed through webcam
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detecting faces in the frame
            faces = detector(gray)

            # locating the landmarks if faces are present
            for face in faces:
                landmarks = predictor(gray, face)
                
                frame = filter(frame, landmarks)

            cv2.imshow('Detector', frame)

            if cv2.waitKey(1) & 0xFF == 27:
                break

        else:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()

