import cv2
import mediapipe as mp
import numpy as np

# Initialize Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.6, model_selection=1)

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer size to decrease lag
cap.set(cv2.CAP_PROP_FPS, 30)  # Ensure max FPS

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    
    # Convert to RGB (Mediapipe expects RGB input)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_detection.process(rgb_frame)
    
    # Track the first detected face
    direction = "PERSON NOT LOCATED"
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = (int(bboxC.xmin * frame.shape[1]), int(bboxC.ymin * frame.shape[0]),
                           int(bboxC.width * frame.shape[1]), int(bboxC.height * frame.shape[0]))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            center_x = x + w // 2
            
            # Determine direction
            if center_x < frame_width // 3:
                direction = "LEFT"
            elif center_x > 2 * frame_width // 3:
                direction = "RIGHT"
            else:
                direction = "FORWARD"
            break  # Only track the first detected face
    
    # Draw text with black background on bottom right
    text_size = cv2.getTextSize(direction, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
    text_x = frame_width - text_size[0] - 20
    text_y = frame_height - 20
    cv2.rectangle(frame, (text_x - 10, text_y - text_size[1] - 10), (text_x + text_size[0] + 10, text_y + 10), (255, 255, 255), -1)
    cv2.putText(frame, direction, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    
    cv2.imshow("Tracking", frame)
    
    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
