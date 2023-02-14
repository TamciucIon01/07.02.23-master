import keras
from PIL import Image
import numpy as np
import time
import os
from skimage import transform
MODEL_FOLDER = "models"
IMAGE_PATH = "infer_image.png"
Classes = {'Apple' : 0, 'Asparagus': 1, 'Aubergine': 2, 'Avocado': 3,
           'Banana': 4, 'Brown_Cap_Mushroom': 5, 'Cabbage': 6,
           'Carrots': 7, 'Cucumber': 8, 'Ginger': 9, 'Juice': 10,
           'Kivi': 11, 'Leek': 12, 'Lemon': 13, 'Lime': 14,
           'Mango': 15, 'Melon': 16, 'Milk': 17, 'Oat_Milk': 18,
           'Oatghurt': 19, 'Onion': 20, 'Orange': 21, 'Passion_fruit': 22,
           'Peach': 23, 'Pear': 24, 'Pepper': 25, 'Pineapple': 26,
           'Pomegranate': 27, 'Potato': 28, 'Red_Beet': 29,
           'Ewd_Grapefruit': 30, 'Satsumas': 31, 'Sour_Cream': 32,
           'Soyghurt': 33, 'Tomato': 34, 'Yoghurt': 35, 'Zucchini': 36,}
Classes = {value : key for (key, value) in Classes.items()}


if 'resnet' not in locals():
    model_path = os.path.join(MODEL_FOLDER, "resnet50_frozen_model")
    resnet = keras.models.load_model(model_path)

def load_labels(path):
    with open(path, 'r') as f:
        return [line.strip() for i, line in enumerate(f.readlines())]

def set_input_tensor(interpreter, image):
    tensor_index = interpreter.get_input_details()[0]['index']
    input_tensor = interpreter.tensor(tensor_index)()[]
    input_tensor[:, :] = image


def classify_images(filename, top_k=5):
    np_image =  Image.open(filename)
    np_image = np.array(np_image).astype('float32')/255
    np_image = transform.resize(np_image, (256, 256, 3))
    np_image = np.expand_dims(np_image, axis=0)

    proba = resnet.predict(mp_image)[0]

    indexes = sorted(range(len(proba)), ley=lambda k: proba[k], reverse=True)

    cuisine_ordered = [Classes[ind] for ind in indexes]
    return cuisine_ordered[:top_k]