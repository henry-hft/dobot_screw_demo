from streamer.Configs import Configs
from streamer.Analysis import Analysis
import threading
import cv2
from flask import Flask, request, jsonify, Response, send_file
import subprocess
import os
from picamera2 import Picamera2
import time

ref_points = None
save_current_frame = False

storage_path = "/home/pi/dobot/images/"
image_name = 'original_foto.jpg'

if not os.path.exists(storage_path):
    os.makedirs(image_name)

class Streamer(Configs):

    def __init__(self):
        self.camera = Picamera2()
        camera_config = self.camera.create_still_configuration(main={"format": 'XRGB8888', "size": Configs.videoResolution})
        self.camera.configure(camera_config)
        self.camera.start()
        self.analysis= Analysis()

    app = Flask(__name__)
    
    """     @app.route("/set_resolution", methods=["POST"])
    def set_resolution(self):
        data = request.get_json()
        new_resolution = data.get("resolution")
        
        if isinstance(new_resolution, tuple) and len(new_resolution) == 2:
            self.resolution = new_resolution
            self.camera_config = self.camera.create_still_configuration(main={"format": 'XRGB8888', "size": self.resolution})
            self.camera.configure(self.camera_config)
            return jsonify({"message": "Auflösung erfolgreich aktualisiert."})
        else:
            return jsonify({"error": "Ungültiges Auflösungsformat."}) """


    def capture_frames(self):
       while (True):
            global ref_points
            frames = self.camera.capture_array()
            global save_current_frame
            if save_current_frame:
                cv2.imwrite(os.path.join(storage_path, image_name), frames)
                save_current_frame =False
                time.sleep (2)

            else:
                image, ref_points = self.analysis.main_analysis(frames)
                with threading.Lock():
                    return_key, encoded_image = cv2.imencode(self.videoEncoding, image)
                    yield(b"--frame\r\n' b'Content-Type: image/jpg\r\n\r\n" + bytearray(encoded_image) + b"\r\n")
            
    def runStream(self):

        app = Flask(__name__)
        
        @app.after_request
        def add_header(response): 
            response.headers["Access-Control-Allow-Origin"] = '*'
            response.headers["Access-Control-Allow-Headers"] = '*'
            response.headers["Access-Control-Allow-Methods"] = '*'
            return response
        
        @app.route('/save_current_frame', methods=['GET'])
        def write_image():
            global save_current_frame 
            save_current_frame = True 
            return jsonify({"message": "write image."})
        
        @app.route('/restart_dobot_server', methods=['GET'])
        def restart_dobot_server():
            command = "sudo systemctl restart dobot_server"
            try:
                output = subprocess.check_output(command, shell=True)
                print("Command executed successfully:")
                print(output.decode())
                return jsonify("Command executed successfully:")
            except subprocess.CalledProcessError as e:
                print("Error executing the command:")
                print(e)
                return jsonify("Error executing the command:")

        
        @app.route('/get_aruco_marker', methods=['GET'])
        def get_ref_points():
            global ref_points
            return jsonify(ref_points)
        
        @app.route("/")
        def streamFrames():
            return Response(self.capture_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

        process_thread = threading.Thread(target=self.capture_frames)
        process_thread.daemon = True
        process_thread.start()
        app.run(self.RaspberryIP, port=self.port, threaded=True)