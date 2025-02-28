import threading
import time
import ev3dev2.motor as motor
import atexit

FILE_PATH = "/home/robot/received_message.txt"

# Initialize motors
left_motor = motor.LargeMotor(motor.OUTPUT_A)
right_motor = motor.LargeMotor(motor.OUTPUT_B)

# Function to stop motors when the program exits
def stop_motors():
    print("Stopping motors (Program exit)...")
    left_motor.off()
    right_motor.off()

# Register exit function
atexit.register(stop_motors)

# Function to control motors
def run_motors():
    print("Motors running...")
    left_motor.on(50)
    right_motor.on(50)

def turn_left():
    left_motor.on(50)
    right_motor.on(-50)

def turn_right():
    left_motor.on(-50)
    right_motor.on(50)




# Function to read commands from file

def read_file():
    print("Listening for SSH messages...")
    while True:
        try:
            with open(FILE_PATH, "r") as file:
                content = file.read().strip()
                print("Content is", content)
                if content:
                    print("Received:", content)
                    process_command(content)
                    open(FILE_PATH, "w").close()  # Clear file after reading

                
        except FileNotFoundError:
            pass

        time.sleep(0.1)  # Check every second

# Function to process commands
def process_command(command):
    if command.lower() == "stop":
        print("Stopping motors!")
        left_motor.off()
        right_motor.off()
    elif command.lower() == "start":
        print("Starting motors!")
        run_motors()
    elif command.lower() == "reverse":
        print("Reversing motors!")
        left_motor.on(-50)
        right_motor.on(-50)
    elif command.lower() == "left":
        print("Left")
        turn_left()
    elif command.lower() == "right":
        print("Right")
        turn_right()

# Start motor thread


# Start file reading thread
try:
    read_file()
except KeyboardInterrupt:
    print("Program interrupted! Stopping motors.")
    stop_motors()
except Exception as e:
    print("Error:", e)
    stop_motors()
