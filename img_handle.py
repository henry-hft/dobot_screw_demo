from PIL import Image
import cv2
import numpy as np


def pres_crop_four_points(image_or_path, marker_coord):
    marker_coord_array = []
    img =cv2.imread (image_or_path)
    
    for marker in marker_coord:
        inner_array = [marker["x"], marker["y"]]
        marker_coord_array.append(inner_array)
    
    print(marker_coord_array)
    rectangle = np.array(marker_coord_array, dtype=np.float32)
    (tl, tr, br, bl) = rectangle

    # Calculate the width and height of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    M = cv2.getPerspectiveTransform(rectangle, dst)
    transformed = cv2.warpPerspective(img, M, (max_width, max_height))

    #transformed_image_path = "./images/"+ 'transformed_image.jpg' 
    #cv2.imwrite(transformed_image_path, transformed)
    return transformed
	

def undistort_image(image_or_path, output_path):
    if isinstance(image_or_path, str):
        img = Image.open(image_or_path)
    elif isinstance(image_or_path, Image.Image):
        img = image_or_path
    else:
        raise ValueError("Invalid input type. Expected image path or PIL Image object.")

    img_array = np.array(img)
    
    camera_matrix = np.array([[4.74169317e+03, 0.00000000e+00, 9.65718408e+02],
                              [0.00000000e+00, 1.47888291e+03, 5.50285164e+02],
                              [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]], dtype=np.float64)

    distortion_coeffs = np.array([0.0, 0.0, 0, 0, 0])


    h, w = img_array.shape[:2]
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, distortion_coeffs, (w, h), 1, (w, h))
    undistorted_image = cv2.undistort(img_array, camera_matrix, distortion_coeffs, None, new_camera_matrix)

    cv2.imwrite(output_path, undistorted_image)
    return undistorted_image



def sort_corners(corners):
    sorted_corners = sorted(corners, key=lambda corner: corner[0][0][1])

    array1 = sorted_corners[0]
    array2 = sorted_corners[1]
    array3 = sorted_corners[2]
    array4 = sorted_corners[3]

    if array1[0][0][0] > array2[0][0][0]:
        array1, array2 = array2, array1

    if array3[0][0][0] < array4[0][0][0]:
        array3, array4 = array4, array3

    return [array1, array2, array3, array4]


def process_frame(frame):

    aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_250)
    aruco_params = cv2.aruco.DetectorParameters_create()

    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(grey, aruco_dict, parameters=aruco_params)
    
    ref_points = []
    if ids is not None and 2 <= len(ids) <= 4:
        if len(ids) == 4:
            corners = sort_corners(corners)
        
        for corner in corners:
            pt = (int(corner[0][0][0]), int(corner[0][0][1]))
            cv2.putText(frame, f'({pt[0]}, {pt[1]})', pt, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 1)
            corner_coord = {
                "x": pt[0],
                "y": pt[1]
            }
            ref_points.append(corner_coord)
        
        for i in range(len(ids) - 1):
            pt1 = (int(corners[i][0][0][0]), int(corners[i][0][0][1]))
            pt2 = (int(corners[i + 1][0][0][0]), int(corners[i + 1][0][0][1]))
            frame = cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        
        pt1 = (int(corners[0][0][0][0]), int(corners[0][0][0][1]))
        pt2 = (int(corners[-1][0][0][0]), int(corners[-1][0][0][1]))
        frame = cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
    
    return frame, ref_points

