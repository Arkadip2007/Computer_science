import cv2
import mediapipe as mp
import pyautogui

# Screen size
screen_w, screen_h = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )

            # Index finger tip
            index_tip = hand_landmarks.landmark[8]
            x = int(index_tip.x * w)
            y = int(index_tip.y * h)

            # Convert camera coords to screen coords
            screen_x = int(index_tip.x * screen_w)
            screen_y = int(index_tip.y * screen_h)

            pyautogui.moveTo(screen_x, screen_y)

            # Thumb tip
            thumb_tip = hand_landmarks.landmark[4]

            # Distance between index & thumb
            dist = abs(index_tip.x - thumb_tip.x) + abs(index_tip.y - thumb_tip.y)

            if dist < 0.05:
                pyautogui.click()
                pyautogui.sleep(0.2)

    cv2.imshow("Mouse Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
