from keras.models import load_model
import dobotserver.image_processing
import cv2
import numpy as np
import os
import re

model = None
classes = ["Schraube 1", "Schraube 2", "Schraube 3"]

def extract_index_from_filename(filename):
    match = re.match(r'^(\d+)_unclassified\.jpg$', filename)
    if match:
        return int(match.group(1))
    return None

def inference(image_paths):
    global model
    if model is None:
        model = load_model('screw_cnn.keras')
    
    for img_path in image_paths:
        #img = cv2.imread(img_path)
        img = image_processing.obj_classification(img_path)
        resized_img = cv2.resize(img, (180, 180))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_array = np.expand_dims(img, axis=0)
        img_array = img_array / 255.0
        
        prediction = model.predict(img_array)
        print(prediction)
        max_index = np.argmax(prediction[0])
        #probabilities = activations_to_percent(prediction)
        
        class_name = classes[max_index]
        filename = os.path.basename(img_path)
        index = extract_index_from_filename(filename)
        if index is not None:
            new_filename = f"{class_name}_{index}_classified.jpg"
            output_path = os.path.join("./images/detail/", new_filename)
            cv2.imwrite(output_path, img)
        else:
            print(f"Could not extract index from filename: {filename}")

