import cv2
import mediapipe as mp
import os
import numpy as np  # Import numpy for creating a blank canvas
import time
from MachineLearning import is_circle  # Import the is_circle function

def run_hand_gesture_detection(output_dir="circle_dataset", output_image_name="drawn_line.png"):
    """
    Run hand gesture detection and save the drawn line image to the specified directory.
    """
    EXIT = False

    # Initialize MediaPipe Hands
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    # Open the webcam
    cap = cv2.VideoCapture(0)

    def count_missing_fingers(hand_landmarks):
        """
        Count the number of missing fingers based on hand landmarks.
        """
        # Define the tips of the fingers
        finger_tips = [8, 12, 16, 20]
        thumb_tip = 4

        # Calculate the palm center as the average of wrist (0) and middle finger MCP (9)
        palm_center_x = (hand_landmarks.landmark[0].x + hand_landmarks.landmark[9].x) / 2
        palm_center_y = (hand_landmarks.landmark[0].y + hand_landmarks.landmark[9].y) / 2

        # Count missing fingers
        missing_fingers = []

        # Check for each finger
        for tip in finger_tips:
            # Check if the tip is below the corresponding lower joint
            if hand_landmarks.landmark[tip].y >= hand_landmarks.landmark[tip - 2].y:
                missing_fingers.append(1)  # Finger is missing
            else:
                missing_fingers.append(0)  # Finger is not missing

        # Check the thumb separately using its position relative to the palm center
        thumb_tip_x = hand_landmarks.landmark[thumb_tip].x
        thumb_tip_y = hand_landmarks.landmark[thumb_tip].y

        # Thumb is considered "missing" if it is too close to the palm center
        if abs(thumb_tip_x - palm_center_x) < 0.1 and abs(thumb_tip_y - palm_center_y) < 0.1:
            missing_fingers.append(1)  # Thumb is missing
        else:
            missing_fingers.append(0)  # Thumb is not missing

        return sum(missing_fingers)

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

                # Count the number of missing fingers
                missing_fingers_count = count_missing_fingers(hand_landmarks)
                print(f"Missing fingers detected: {missing_fingers_count}")  # Debugging output
                cv2.putText(frame, f"Missing Fingers: {missing_fingers_count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # If 1 missing finger is detected, track the tip of the index finger (landmark 8)
                if missing_fingers_count == 4:
                    index_finger_tip = hand_landmarks.landmark[8]
                    h, w, _ = frame.shape
                    x, y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)

                    # Check if the distance to the last point is within a threshold
                    if finger_tip_points:
                        last_x, last_y = finger_tip_points[-1]
                        distance = np.sqrt((x - last_x) ** 2 + (y - last_y) ** 2)
                        if distance < 50:  # Threshold to prevent jumping
                            finger_tip_points.append((x, y))
                            print(f"Point added: ({x}, {y})")  # Debugging output
                            # Draw the line connecting the points on the line canvas
                            cv2.line(line_canvas, (last_x, last_y), (x, y), (255, 0, 0), 2)
                        else:
                            print(f"Hand moved too far, resetting points.")  # Debugging output
                            finger_tip_points.clear()  # Clear points to start a new segment
                            finger_tip_points.append((x, y))  # Add the new starting point
                    else:
                        finger_tip_points.append((x, y))
                        print(f"First point added: ({x}, {y})")  # Debugging output

                # If no missing fingers are detected, save the drawn line as an image and refresh the line
                if missing_fingers_count == 5:
                    if len(finger_tip_points) > 1:  # Ensure there are points to save
                        # Save the line canvas as an image
                        output_path = os.path.join(output_dir, output_image_name)
                        cv2.imwrite(output_path, line_canvas)
                        print(f"Line image saved to {output_path}", flush=True)  # Debugging output
                    else:
                        print("No points to save, skipping image save.")  # Debugging output

                    # Clear the points to refresh the line
                    finger_tip_points.clear()
                    print("Cleared finger tip points.")  # Debugging output

                    # Reset the line canvas
                    line_canvas = np.zeros_like(frame)

                    EXIT = True

        # Overlay the line canvas on the frame for display
        combined_frame = cv2.addWeighted(frame, 0.8, line_canvas, 0.2, 0)

        # Display the frame
        cv2.imshow("Hand Gesture Detection", combined_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q') or EXIT:
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_hand_gesture_detection()