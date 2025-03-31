import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import os

def is_circle(image_path):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    # Preprocess the image
    image = cv2.resize(image, (64, 64))  # Resize to a fixed size
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extract features (e.g., contour area, perimeter, circularity)
    features = []
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0 or area == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter ** 2))
        bounding_rect = cv2.boundingRect(contour)
        aspect_ratio = bounding_rect[2] / bounding_rect[3]  # Width / Height
        features.append([area, perimeter, circularity, aspect_ratio])
    
    if not features:
        return {"is_circle": False, "confidence": 0.0}
    
    # Use the largest contour's features for evaluation
    features = np.array(max(features, key=lambda x: x[0])).reshape(1, -1)
    
    # Load or train a simple model
    model_path = "circle_detector_model.pkl"
    if os.path.exists(model_path):
        import joblib
        model = joblib.load(model_path)
    else:
        # Train a simple model (for demonstration purposes)
        X_train = np.array([
            [1000, 120, 1.0, 1.0],  # Circle example
            [500, 80, 0.5, 1.2],   # Non-circle example
            [1500, 140, 0.9, 1.0], # Circle example
            [400, 70, 0.4, 1.3]    # Non-circle example
        ])
        y_train = np.array([1, 0, 1, 0])  # 1 for circle, 0 for not circle
        model = make_pipeline(StandardScaler(), SVC(probability=True))
        model.fit(X_train, y_train)
        import joblib
        joblib.dump(model, model_path)
    
    # Predict if the image is a circle
    prediction = model.predict(features)
    confidence = model.predict_proba(features)[0][1]  # Probability for "circle" class
    
    return {"is_circle": bool(prediction[0]), "confidence": confidence}

# Example usage
if __name__ == "__main__":
    result = is_circle("drawn_line_only.png")
    print(f"Is Circle: {result['is_circle']}, Confidence: {result['confidence']:.2f}")