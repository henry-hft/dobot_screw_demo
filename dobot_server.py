from dobot_handler import dobot_handler
from flask import Flask, request, jsonify, Response, send_from_directory
import time
import json
import threading
import os
import image_processing
import img_handle
import control
import classification_cnn
import glob

file_write_lock = threading.Lock()
app = Flask(__name__)

dobot = None
obj_pixel_coord = None
calib_values = None
get_position_flag = True
stop_process_flag = None

# Function to write JSON data to a file
def write_to_file(data, filename):
    with file_write_lock:
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

# Set calibration values
def set_calibration_values():
    with open("calibration_file.json") as json_file:
        global calib_values
        calib_values = json.load(json_file)
    return jsonify({"message": "Calibration values set."})

def initialize_dobot(dobot_ip="192.168.1.6", speed=80):
    global dobot
    try:
        dobot = dobot_handler(dobot_ip)
        return True, "Connection established"
    except Exception as error:
        return False, "Connection failed"


# Initialize Dobot before the first request
def setup_dobot():
    success, message = initialize_dobot()
    if success:
        dobot.start()
    else:
        return message

def setup_calibration():
     with open("calibration_file.json") as json_file:
        global calib_values
        calib_values = json.load(json_file)
 

@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    return response

@app.route('/')
def index():
    #classification_cnn.inference("images/1.jpg")
    return send_from_directory('html', 'index.html')

@app.route('/<path:path>')
def send_html(path):
    return send_from_directory('html', path)

""" # Stop the process
@app.route('/stop_process', methods=['GET'])
def stopProcess():
    global stop_process_flag
    stop_process_flag = True
    print(stop_process_flag, 'in the server')
    return jsonify({"message": "stop process."}) """

# Clear Dobot error
@app.route("/clear_error", methods=["GET"])
def clearError():
    dobot.dashboard.ClearError()
    time.sleep(2)
    return jsonify({"message": "Clear Error"})

# reset Dobot
@app.route("/reset_dobot", methods=["GET"])
def resetDobot():
    dobot.dashboard.ResetRobot()
    time.sleep(2)
    return jsonify({"message": "rest dobot"})


# Get Dobot error ID
@app.route("/get_error_id", methods=["GET"])
def getErrorId():
    return jsonify({"errorIds": dobot.dashboard.GetErrorID()})


# Enable Dobot
@app.route("/enable", methods=["GET"])
def enableRobot():
    try:
        dobot.dashboard.ClearError ()
        dobot.dashboard.EnableRobot(0.325, 0.0, 0.0, 0.0)
        return jsonify({"message": "Dobot is enabled"})
    except Exception as e:
        return jsonify({"error": str(e)})


# Disable Dobot
@app.route("/disable", methods=["GET"])
def disableRobot():
    dobot.dashboard.DisableRobot()
    return jsonify({"message": "Dobot is disabled"})


# Get Dobot mode
@app.route("/get_dobot_mode", methods=["GET"])
def getDobotMode():
    return jsonify({"mode": dobot.dashboard.RobotMode()})


@app.route("/open_gripper", methods=["GET"])
def open_gripper():
    dobot.setDO(8, 1)
    return jsonify({"message": "open gripper"})

@app.route("/close_gripper", methods=["GET"])
def close_gripper():
    dobot.setDO(8, 0)
    return jsonify({"message": "close Gripper"})


@app.route("/get_dobot_position", methods=["GET"])
def get_dobot_position():
    try:
        dobot_position = dobot.dashboard.GetPose()
        return jsonify({"position": dobot_position})
    except Exception as e:
        return jsonify({"error": str(e)})
    
# Move to start photo position
@app.route("/move_to_start_foto_pos", methods=["POST"])
def move_to_start_foto_pos():
    dobot.dashboard.EnableRobot(0.325, 0.0, 0.0, 0.0)

    dobot_coords = request.get_json()
    if dobot_coords:
        dobot.moveToPoint([dobot_coords["x"], dobot_coords["y"], dobot_coords["z"], dobot_coords["r"]])
        time.sleep(2)
    else:
        x = float(calib_values['dobot_foto_pos']['x'])
        y = float(calib_values['dobot_foto_pos']['y'])
        z = float(calib_values['dobot_foto_pos']['z'])
        r = float(calib_values['dobot_foto_pos']['r'])
        dobot.moveToPoint([x, y, z, r])
        time.sleep(2)

    dobot.dashboard.DisableRobot()
    return jsonify({"message": "Moved to start photo position"})


# Save calibration file
@app.route("/save_calibration_file", methods=["POST"])
def save_calibration_file():
    data = request.get_json()
    threading.Thread(target=write_to_file, args=(data, "calibration_file.json")).start()
    response_data = {"message": "Received JSON object and started processing."}
    time.sleep(2)
    set_calibration_values()
    return jsonify(response_data), 200

# Save camera settings
@app.route("/save_camera_settings", methods=["POST"])
def save_camera_settings():
    data = request.get_json()
    threading.Thread(
        target=write_to_file, args=(data, "camera_settings_file.json")
    ).start()
    response_data = {"message": "Received JSON object and started processing."}
    return jsonify(response_data), 200


# Save Dobot settings
@app.route("/send_dobot_params", methods=["POST"])
def send_dobot_params():
    data = request.get_json()
    threading.Thread(target=write_to_file, args=(data, "dobot_settings.json")).start()
    response_data = {"message": "Received JSON object and started processing."}
    return jsonify(response_data), 200


# Get image by name
@app.route("/get_image/<path:image_path>", methods=["GET"])
def get_image(image_path):
    def generate():
        full_image_path = os.path.join("./images", image_path)
        with open(full_image_path, "rb") as img_file:
            chunk_size = 1024
            while True:
                chunk = img_file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    return Response(generate(), mimetype="image/jpeg")


# get all classified images
@app.route("/list_detail_images", methods=["GET"])
def list_detail_images():
    folder_path = './images/detail'
    files = os.listdir(folder_path)
    return jsonify(files)


# Find contours
@app.route("/find_contours", methods=["GET"])
def find_contours():
    set_calibration_values()
    marker_coord = calib_values["marker_coord"]
    print (marker_coord, '*************************************')
    global obj_pixel_coord
    trans_foto = img_handle.pres_crop_four_points(
        "./images/original_foto.jpg", marker_coord
    )
    
    obj_pixel_coord = image_processing.obj_recognition(trans_foto)
    return jsonify({"message": "Contours detection started."})


# Classify Objects
@app.route("/classify_objects", methods=["GET"])
def classify_objects():
    unclassified_images = [datei for datei in glob.glob(os.path.join("./images/detail/", '*unclassified*'))]
    classification_cnn.inference(unclassified_images)
    return jsonify(unclassified_images)


# Start the process
@app.route("/start_process", methods=["GET"])
def start_process():
    dobot.dashboard.EnableRobot(0.500, 0.0, 0.0, 0.0)

    world_coord = control.prep_coords(
        list(obj_pixel_coord.values()), calib_values
    )
    foto_postion = calib_values["dobot_foto_pos"]
    dobot_mode = dobot.dashboard.RobotMode()
    if (dobot_mode != 9 ):
     control.move_to_object(world_coord, -138, -90.50, dobot, foto_postion)
    

if __name__ == "__main__":
    #app.run(host="192.168.11.151", port=5000)
    setup_dobot()
    setup_calibration()
    app.run(host='0.0.0.0', port=5000)
