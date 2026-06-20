import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# ------------------ Safety ------------------
pyautogui.FAILSAFE = True

# ------------------ Screen ------------------
screen_w, screen_h = pyautogui.size()

# ------------------ Camera ------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# ------------------ MediaPipe ------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,          # FPS boost
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

# ------------------ Helpers ------------------
def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

# smoothing
prev_x, prev_y = 0, 0
smooth = 6

# rate limit
last_click = 0
last_scroll = 0

# ------------------ Loop ------------------
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        hand = result.multi_hand_landmarks[0]
        lm = hand.landmark
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # landmarks
        thumb = lm[4]
        index = lm[8]
        middle = lm[12]
        ring = lm[16]

        # finger up logic
        index_up = index.y < lm[6].y
        middle_up = middle.y < lm[10].y
        ring_up = ring.y < lm[14].y

        # # ------------------ Emergency STOP ------------------
        # if not index_up and not middle_up and not ring_up:
        #     print("STOP")
        #     break

        # ------------------ Mouse Move (Index only) ------------------
        if index_up and not middle_up:
            ix, iy = int(index.x * w), int(index.y * h)

            sx = np.interp(ix, (0, w), (0, screen_w))
            sy = np.interp(iy, (0, h), (0, screen_h))

            # smoothing
            curr_x = prev_x + (sx - prev_x) / smooth
            curr_y = prev_y + (sy - prev_y) / smooth

            pyautogui.moveTo(curr_x, curr_y)

            prev_x, prev_y = curr_x, curr_y

        now = time.time()

        # ------------------ Left Click (Index + Thumb) ------------------
        if dist(index, thumb) < 0.03 and now - last_click > 0.4:
            pyautogui.click()
            last_click = now

        # ------------------ Right Click (Index + Middle) ------------------
        if dist(index, middle) < 0.03 and now - last_click > 0.4:
            pyautogui.rightClick()
            last_click = now

        # ------------------ Drag ------------------
        if dist(index, thumb) < 0.02:
            pyautogui.mouseDown()
        else:
            pyautogui.mouseUp()

        # ------------------ Scroll (3 fingers) ------------------
        if index_up and middle_up and ring_up and now - last_scroll > 0.15:
            if index.y < lm[6].y:
                pyautogui.scroll(40)
            else:
                pyautogui.scroll(-40)
            last_scroll = now

    cv2.imshow("Mouse Control (ESC / q to quit)", frame)

    key = cv2.waitKey(1)
    if key == 27 or key == ord('q'):   # ESC or q
        break

# ------------------ Cleanup ------------------
cap.release()
cv2.destroyAllWindows()
