import numpy as np 
import time
from dobot_handler import dobot_handler

def calculate_rotation_factor(angle_list, rotation_list):
    if len(angle_list) != len(rotation_list):
        raise ValueError("The input lists must have the same length.")
    
    angle_array = np.array(angle_list)
    rotation_array = np.array(rotation_list)
    
    m, b = np.polyfit(angle_array, rotation_array, 1)
    
    return m, b

angle_list = [90, 42 , 2, -45, 90, 25, -10, -41]
rotation_list = [37, 175, 128, -97, 37, 155, -69, -96]

slope, y_intercept = calculate_rotation_factor(angle_list, rotation_list)

def calculate_rotation(angle):
    return slope * angle + y_intercept + 114

def filter_objects_coor(points_map):
    return list(points_map.values())

# calculate the distances between the points
def calculate_distances(calib_values):
    dobot_ref_points = calib_values['ref_points']
    marker_coord = calib_values['marker_coord']
    
    start_x =float(dobot_ref_points['x1'])
    start_y =float(dobot_ref_points['y1'])
     
    d_dobot_x = abs(float(dobot_ref_points['x2']) - float(dobot_ref_points['x1']))
    d_dobot_y = abs(float(dobot_ref_points['y3']) - float(dobot_ref_points['y2']))

    d_ref_y = abs(marker_coord[3]['y'] - marker_coord[0]['y'])
    d_ref_x = abs(marker_coord[2]['x'] - marker_coord[3]['x'])

    result = {
        'dobot_start': (start_x,start_y),
        'd_dobot_x': d_dobot_x,
        'd_dobot_y': d_dobot_y,
        'd_ref_x': d_ref_x,
        'd_ref_y': d_ref_y
    }
    return result

# calculate dobot coordiante
def calc_dobot(obj_coord, start_coor, d_ref_x, d_ref_y, d_dobot_x, d_dobot_y):
    dobot_coords = []
    start_x = float(start_coor[0]) 
    start_y = float(start_coor[1]) 
    
    for data in obj_coord:
        x, y = data[0]
        rotation = data[1]
        color = data[2]
        print(d_ref_y)
        print(d_ref_x)
        dobot_x = start_x  + (y / d_ref_y * d_dobot_x) 
        dobot_y = start_y + (x/ d_ref_x * d_dobot_y) 
        dobot_coords.append([dobot_x, dobot_y, rotation, color])

    return dobot_coords

# function to prepare the coordinate
def prep_coords(obj_coords, calib_value):

    d_cali_value = calculate_distances(calib_value)
    print(d_cali_value['d_ref_y'])
    world_coord = calc_dobot(obj_coords, d_cali_value['dobot_start'], d_cali_value['d_ref_x'], 
                              d_cali_value['d_ref_y'], d_cali_value['d_dobot_x'], d_cali_value['d_dobot_y'])  
    
    return world_coord

def get_drop_position(color):
    drop_positions = {
        'Schwarz': [318, 285, -111, 108],
        'Grau': [244, -301, -111, 19],
        'Other': [177, 292, -111, 125]
    }
    return drop_positions.get(color, drop_positions['Other'])

def move_to_pick_position(dobot: dobot_handler, x, y, rotation, height):
    dobot.moveToPoint([x, y, height, rotation + 8])
    time.sleep(1)

def close_gripper_pick(dobot: dobot_handler, x, y, rotation, height_top, height_down):
    move_to_pick_position(dobot, x, y, rotation, height_top)
    move_to_pick_position(dobot, x, y, rotation, height_down)
    dobot.setDO(8, 0) # close gripper
    move_to_pick_position(dobot, x, y, rotation, height_top)

def move_to_drop_position(dobot: dobot_handler, drop_pos):
    dobot.moveToPoint(drop_pos)
    #clf.MovJ(*drop_pos)
    time.sleep(1)

def move_to_photo_position(dobot: dobot_handler, x, y, z = 100):
    dobot.moveToPoint([x, y, z, 0])
    time.sleep(1)

def move_to_object(dobot_coord, height_down, height_top, dobot: dobot_handler, photo_position):
    dobot.setDO(8, 1)
    time.sleep(0.5)
    ##stop_flag = False
    for x, y, rotation, color in dobot_coord:
        if(x > 205 ):
            drop_pos = get_drop_position(color)
            rotation = calculate_rotation(rotation)
            x_adjustment = 2
            x += x_adjustment 
            y_adjustment = 2.8 if (y > 50 or y < -50) else 2
            y += y_adjustment
           
            move_to_pick_position(dobot, x, y, rotation, height_top)
            close_gripper_pick(dobot, x, y, rotation, height_top, height_down)
            move_to_drop_position(dobot, drop_pos)
            dobot.setDO(8, 1)
    
    dobot.moveToPoint([photo_position["x"], photo_position["y"], photo_position["z"], 35])
    time.sleep(2)
    dobot.dashboard.DisableRobot()