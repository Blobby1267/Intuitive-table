import HandGestures as hg  # Import the function from handgestures
import MachineLearning as ml

hg.run_hand_gesture_detection()
result = ml.is_circle()

print("\n\n---------------------------------")
print(f"Is Circle: {result['is_circle']}, Confidence: {result['confidence']:.2f}")
print("---------------------------------\n\n")