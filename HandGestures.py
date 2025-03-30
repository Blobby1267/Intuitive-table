import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Open the webcam
cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    """
    Count the number of raised fingers based on hand landmarks.
    """
    # Define the tips of the fingers
    finger_tips = [8, 12, 16, 20]
    thumb_tip = 4

    # Count fingers
    fingers = []

    # Check for each finger
    for tip in finger_tips:
        # Check if the tip is above the corresponding lower joint
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers.append(1)  # Finger is raised
        else:
            fingers.append(0)  # Finger is not raised

    # Check the thumb separately (horizontal and vertical movement)
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x and \
       abs(hand_landmarks.landmark[thumb_tip].y - hand_landmarks.landmark[thumb_tip - 1].y) < 0.05:
        fingers.append(1)  # Thumb is raised
    else:
        fingers.append(0)  # Thumb is not raised

    return sum(fingers)

# Initialize a list to store finger tip points for drawing line
finger_tip_points = []


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Flip the frame horizontally for a mirror-like effect
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe Hands
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand landmarks on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Count the number of raised fingers
            fingers_count = count_fingers(hand_landmarks)
            print(f"Fingers detected: {fingers_count}")  # Debugging output
            cv2.putText(frame, f"Fingers: {fingers_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Print "Hello" if fingers_count is 4
            if fingers_count == 4:
                index_finger_tip = hand_landmarks.landmark[8]
                h, w, _ = frame.shape
                x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                finger_tip_points.append((x, y))

                # Draw the line connecting the points
                for i in range(1, len(finger_tip_points)):
                    cv2.line(frame, finger_tip_points[i - 1], finger_tip_points[i], (255, 0, 0), 2)

    # Display the frame
    cv2.imshow("Hand Gesture Detection", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()