import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import os
import glob

def preprocess_image(image_path):
    # Load and preprocess a single image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    image = cv2.resize(image, (64, 64))
    _, thresh = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    features = []
    for contour in contours:
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0 or area == 0:
            continue
        circularity = 4 * np.pi * (area / (perimeter ** 2))
        bounding_rect = cv2.boundingRect(contour)
        aspect_ratio = bounding_rect[2] / bounding_rect[3]
        features.append([area, perimeter, circularity, aspect_ratio])
    if not features:
        return None
    return max(features, key=lambda x: x[0])  # Use the largest contour's features

def load_dataset(dataset_path):
    # Load and preprocess the dataset
    X, y = [], []
    for label in ["circle", "non_circle"]:
        label_path = os.path.join(dataset_path, label)
        for image_path in glob.glob(os.path.join(label_path, "*.png")):
            features = preprocess_image(image_path)
            if features is not None:
                X.append(features)
                y.append(1 if label == "circle" else 0)
    return np.array(X), np.array(y)

def is_circle(image_path):
    # Load or train the model
    model_path = "circle_detector_model.pkl"
    if os.path.exists(model_path):
        import joblib
        model = joblib.load(model_path)
    else:
        dataset_path = "circle_dataset"  # Path to the dataset
        X_train, y_train = load_dataset(dataset_path)
        model = make_pipeline(StandardScaler(), SVC(probability=True))
        model.fit(X_train, y_train)
        import joblib
        joblib.dump(model, model_path)
    
    # Preprocess the input image
    features = preprocess_image(image_path)
    if features is None:
        return {"is_circle": False, "confidence": 0.0}
    features = np.array(features).reshape(1, -1)
    
    # Predict if the image is a circle
    prediction = model.predict(features)
    confidence = model.predict_proba(features)[0][1]  # Probability for "circle" class
    
    return {"is_circle": bool(prediction[0]), "confidence": confidence}

# Example usage
if __name__ == "__main__":
    result = is_circle("drawn_line_only.png")
    print(f"Is Circle: {result['is_circle']}, Confidence: {result['confidence']:.2f}")