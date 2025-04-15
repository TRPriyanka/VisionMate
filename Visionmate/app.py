import subprocess
from flask import Flask, render_template
import pyttsx3
import threading
import time

app = Flask(__name__)

# Global variable to store the process
vision_process = None

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)

# Function to speak messages in a separate thread
def speak(message):
    threading.Thread(target=lambda: (engine.say(message), engine.runAndWait())).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start-detection', methods=['GET'])
def start_detection():
    global vision_process
    if vision_process is None or vision_process.poll() is not None:  # If no process is running
        try:
            vision_process = subprocess.Popen(["python", "vision.py"])
            return "Vision detection has been started!", 200
        except Exception as e:
            return f"Error starting vision detection: {e}", 500
    else:
        return "Vision detection is already running.", 400

@app.route('/stop-detection', methods=['GET'])
def stop_detection():
    global vision_process
    if vision_process:
        try:
            if vision_process.poll() is None:  # If process is running
                print("Stopping vision detection process...")
                vision_process.terminate()  # Try to terminate first
                time.sleep(1)  # Give it some time
                if vision_process.poll() is None:  # If still running, force kill
                    vision_process.kill()
                vision_process.wait()  # Wait for process to close
                vision_process = None  # Reset process variable
                
                # Speak after the vision process is stopped
                speak("Vision detection stopped.")
                
                return "Vision detection has been stopped.", 200
            else:
                return "Vision detection is not running.", 400
        except Exception as e:
            return f"Error stopping vision detection: {e}", 500
    else:
        return "No vision detection is currently running.", 400

if __name__ == '__main__':
    app.run(debug=False)
