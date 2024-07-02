import cv2
import base64
from ultralytics import YOLO
import math
import pymongo
from datetime import datetime
import sys

# Ensure the user's email is passed as a command-line argument
if len(sys.argv) < 2:
    print("Usage: python script.py <user_email>")
    sys.exit(1)

user_email = sys.argv[1]

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["masters"]
users_collection = db["users"]

camera_ids = [0]

captures = []

# Open and configure the cameras
for i in camera_ids:
    cap = cv2.VideoCapture(i)
    cap.set(3, 1200)
    cap.set(4, 720)
    captures.append(cap)

model = YOLO('bestnew.pt')

classNames = ['elephant']
classColors = [(0, 255, 0)]

# Convert alarm.wav to base64
with open('alarm.wav', 'rb') as file:
    sound_data = file.read()
sound_base64 = base64.b64encode(sound_data).decode('utf-8')

while True:
    # Iterate through each camera and perform detection
    for i, cap in enumerate(captures):
        success, img = cap.read()
        results = model(img, stream=True)

        boxes_detected = False  # Flag to track if any boxes were detected

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1

                # Get class index
                cls = int(box.cls[0])

                # Get class name and color
                animal_name = classNames[cls]
                color = classColors[cls]

                # Calculate confidence
                conf = math.ceil((box.conf[0] * 100)) / 100

                # Check if confidence is above the threshold
                if conf >= 0.6:
                    # Draw bounding box with class color
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

                    # Draw class name and confidence
                    cv2.putText(img, f'{animal_name} {conf}', (max(0, x1), max(35, y1)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                    if i == 0:
                        areas = "area1"
                    elif i == 1:
                        areas = "area2"
                    elif i == 2:
                        areas = "area3"

                    # Get the animal image within the bounding box
                    animal_image = img[y1:y2, x1:x2]

                    # Convert the image to base64 string
                    _, image_buffer = cv2.imencode('.jpg', animal_image)
                    image_base64 = base64.b64encode(image_buffer).decode('utf-8')

                    # Create detection data
                    current_time = datetime.now().strftime("%Y-%m-%d,%H:%M:%S")
                    detection_data = {
                        "documentno": "first",
                        "area_name": areas,
                        "animal_name": animal_name,
                        "confidence": conf,
                        "time": current_time,
                        "animal_image": image_base64,
                        "sound_file": sound_base64  # Add sound file as base64
                    }

                    # Update user's document with detection data
                    users_collection.update_one(
                        {"email": user_email},
                        {"$push": {"detections": detection_data}}
                    )

                    boxes_detected = True  # Set flag indicating boxes were detected

        if not boxes_detected:
            # Draw "No Detection" message
            cv2.putText(img, 'No Detection', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
            detection_data = {
                "documentno": "second",
                "no_detection": "No Animal Present Near Railway Track"
            }

            # Update user's document with no detection data
            users_collection.update_one(
                {"email": user_email},
                {"$push": {"detections": detection_data}}
            )

        cv2.imshow(f"Camera {i}", img)

    # exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release all the captures and close windows
for cap in captures:
    cap.release()

cv2.destroyAllWindows()
