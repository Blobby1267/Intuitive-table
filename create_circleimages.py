import os
import HandGestures as hg  # Import the function from handgestures


while True:
    # Define the path to the "circle" folder
    circle_folder_path = os.path.join(os.getcwd(), "circle_dataset/circle")

    # Count the number of files in the "circle" folder
    if os.path.exists(circle_folder_path) and os.path.isdir(circle_folder_path):
        file_count = len([f for f in os.listdir(circle_folder_path) if os.path.isfile(os.path.join(circle_folder_path, f))])
        counter = file_count + 1
    else:
        counter = 1  # Default to 1 if the folder doesn't exist

    # Generate the filename using the counter
    filename = f"circle{counter}.png"
    
    # Call the handgestures function with the generated filename
    hg.run_hand_gesture_detection("circle_dataset/circle", filename)
    # Check if the user wants to quit
    user_input = input("Press 'q' to quit or any other key to continue: ")
    if user_input.lower() == 'q':
        break