import cv2
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import os
import glob

# Ensure the "machine_learning" directory exists
BASE_DIR = "machine_learning"
os.makedirs(BASE_DIR, exist_ok=True)

def preprocess_image(image_path):
    # Load and preprocess a single image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    try:
        # Standardize resizing to a fixed size
        image = cv2.resize(image, (128, 128))
        
        # Normalize pixel values
        image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
        
        # Apply Otsu's thresholding for consistency
        _, thresh = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Save the thresholded image for debugging
        debug_dir = os.path.join(BASE_DIR, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, os.path.basename(image_path))
        cv2.imwrite(debug_path, thresh)
        
        # Extract contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
        
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
        
        # Use the largest contour's features
        largest_feature = max(features, key=lambda x: x[0])
        return largest_feature
    except Exception:
        return None

def load_dataset(dataset_path):
    # Load and preprocess the dataset
    X, y = [], []
    for label in ["circle", "non_circle"]:
        label_path = os.path.join(dataset_path, label)
        if not os.path.exists(label_path):
            raise FileNotFoundError(f"Directory not found: {label_path}")
        image_files = glob.glob(os.path.join(label_path, "*.png"))
        for image_path in image_files:
            features = preprocess_image(image_path)
            if features is not None:
                X.append(features)
                y.append(1 if label == "circle" else 0)
    if not X or not y:
        raise ValueError("Dataset is empty or improperly formatted.")
    return np.array(X), np.array(y)

def is_circle(image_path="circle_dataset/drawn_line.png"):
    # Load or train the model
    model_path = os.path.join(BASE_DIR, "circle_detector_model.pkl")
    if os.path.exists(model_path):
        import joblib
        model = joblib.load(model_path)
    else:
        dataset_path = "circle_dataset"  # Path to the dataset
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset path not found: {dataset_path}")
        X_train, y_train = load_dataset(dataset_path)
        model = make_pipeline(StandardScaler(), SVC(probability=True))
        model.fit(X_train, y_train)
        import joblib
        joblib.dump(model, model_path)
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image path not found: {image_path}")
    
    # Preprocess the input image
    features = preprocess_image(image_path)
    if features is None:
        return {"is_circle": False, "confidence": 0.0}
    features = np.array(features).reshape(1, -1)
    
    # Predict if the image is a circle
    prediction = model.predict(features)
    confidence = model.predict_proba(features)[0][1]  # Probability for "circle" class
    
    # Require confidence of at least 0.7 to classify as a circle
    return {"is_circle": bool(prediction[0])and confidence >= 0.7, "confidence": confidence}

# Example usage
if __name__ == "__main__":
    test_image_path = "circle_dataset/drawn_line.png"  # Update with a valid test image path
    if not os.path.exists(test_image_path):
        raise FileNotFoundError(f"Test image not found: {test_image_path}")
    result = is_circle(test_image_path)
    print(f"Is Circle: {result['is_circle']}, Confidence: {result['confidence']:.2f}")