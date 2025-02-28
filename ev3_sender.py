import cv2
import mediapipe as mp
import numpy as np
import paramiko
from time import time, sleep

EV3_IP = "ev3dev.local"
USERNAME = "robot"
PASSWORD = "maker"

message = "stop"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


try:
    client.connect(EV3_IP, username=USERNAME, password=PASSWORD)
    
except Exception as e:
    print("SSH Error:", e)

transport = client.get_transport()
channel = transport.open_session()
channel.get_pty()
channel.invoke_shell()



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
    direction = "stop"
    if results.detections:
        for detection in results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = (int(bboxC.xmin * frame.shape[1]), int(bboxC.ymin * frame.shape[0]),
                           int(bboxC.width * frame.shape[1]), int(bboxC.height * frame.shape[0]))
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            center_x = x + w // 2
            
            # Determine direction
            if center_x < frame_width // 3:
                direction = "right"
            elif center_x > 2 * frame_width // 3:
                direction = "left"
            else:
                direction = "stop"
            break  # Only track the first detected face

    print(f"Start sending at {time()}")
    #stdin, stdout, stderr = client.exec_command(f'echo "{direction}" > received_message.txt')
    channel.send(f'echo "{direction}" > received_message.txt\n')
    
    
    print(f"End sending at {time()}")
    sleep(0.1)
    
    # Print the command to the console
    print("Command:", direction)
    
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