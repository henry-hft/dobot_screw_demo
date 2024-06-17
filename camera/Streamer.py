from camera.Configs import Configs
from camera.Analysis import Analysis
import threading
import cv2
from flask import Flask, request, jsonify, Response, send_file
import subprocess
import os
from picamera2 import Picamera2
import time
from libcamera import controls

ref_points = None
save_current_frame = False
save_current_frame_detail = False
frame_detail_index = 0
current_lens_position = 2.0

storage_path = "/home/pi/dobot3_2024/dobot/images/"
storage_path_detail = "/home/pi/dobot3_2024/dobot/images/detail/"
image_name = 'original_foto.jpg'

if not os.path.exists(storage_path):
    os.makedirs(storage_path)

class Streamer(Configs):

    def __init__(self):
        self.camera = Picamera2()
        resolution = (1920, 1080)
        camera_config = self.camera.create_still_configuration(main={"format": 'XRGB8888', "size": resolution})
        self.camera.configure(camera_config)
        self.camera.start()
        self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": 2.0})
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
        while True:
            global ref_points
            global current_lens_position
            global save_current_frame
            global save_current_frame_detail

            frames = self.camera.capture_array()

            if save_current_frame:
                if current_lens_position != 2.0:
                    current_lens_position = 2.0
                    self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": current_lens_position})
                    time.sleep(3)
                else:
                    cv2.imwrite(os.path.join(storage_path, image_name), frames)
                    save_current_frame = False
            elif save_current_frame_detail:
                if current_lens_position != 10.0:
                    current_lens_position = 10.0
                    self.camera.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition": current_lens_position})
                    time.sleep(3)
                else:
                    global frame_detail_index
                    frame_detail_index += 1
                    cv2.imwrite(os.path.join(storage_path_detail, str(frame_detail_index) + "_unclassified.jpg"), frames)
                    save_current_frame_detail = False

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

        @app.route('/save_current_frame_detail', methods=['GET'])
        def write_detail_image():
            global save_current_frame_detail
            save_current_frame_detail = True 
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
