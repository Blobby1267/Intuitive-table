import cv2
import mediapipe as mp
import os
import numpy as np  # Import numpy for creating a blank canvas
import time

def run_hand_gesture_detection():

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

    # Initialize a blank image for drawing the line
    line_canvas = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Flip the frame horizontally for a mirror-like effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Initialize the line canvas to match the frame size
        if line_canvas is None:
            line_canvas = np.zeros_like(frame)

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

                # If 4 fingers are detected, track the tip of the index finger (landmark 8)
                if fingers_count == 4:
                    index_finger_tip = hand_landmarks.landmark[8]
                    h, w, _ = frame.shape
                    x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
                    finger_tip_points.append((x, y))
                    print(f"Point added: ({x}, {y})")  # Debugging output

                    # Draw the line connecting the points on the line canvas
                    for i in range(1, len(finger_tip_points)):
                        cv2.line(line_canvas, finger_tip_points[i - 1], finger_tip_points[i], (255, 0, 0), 2)

                # If 5 fingers are detected, save the drawn line as an image and refresh the line
                if fingers_count == 5:
                    if len(finger_tip_points) > 1:  # Ensure there are points to save
                        # Save the line canvas as an image
                        output_path = os.path.join(os.getcwd(), "drawn_line_only.png")
                        cv2.imwrite(output_path, line_canvas)
                        print(f"Line image saved to {output_path}", flush=True)  # Debugging output
                    else:
                        print("No points to save, skipping image save.")  # Debugging output

                    # Clear the points to refresh the line
                    finger_tip_points.clear()
                    print("Cleared finger tip points.")  # Debugging output

                    time.sleep(2)

                    # Reset the line canvas
                    line_canvas = np.zeros_like(frame)

        # Overlay the line canvas on the frame for display
        combined_frame = cv2.addWeighted(frame, 0.8, line_canvas, 0.2, 0)

        # Display the frame
        cv2.imshow("Hand Gesture Detection", combined_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

run_hand_gesture_detection()