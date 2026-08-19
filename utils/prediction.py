import os

# ============================================================
# FORCE TENSORFLOW TO USE CPU
# ============================================================

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"


import numpy as np
import tensorflow as tf
from PIL import Image


# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "road_pothole_mobilenetv2.keras"
)


# ============================================================
# CLASS NAMES
# ============================================================

CLASS_NAMES = [
    "Large pothole",
    "Normal",
    "Small pothole"
]


# ============================================================
# LOAD MODEL
# ============================================================

model = tf.keras.models.load_model(
    MODEL_PATH
)


# ============================================================
# IMAGE PREDICTION
# ============================================================

def predict_image(image):

    image = image.convert("RGB")

    image = image.resize(
        (224, 224)
    )

    image_array = tf.keras.preprocessing.image.img_to_array(
        image
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    predictions = model.predict(
        image_array,
        verbose=0
    )[0]

    predicted_index = int(
        np.argmax(predictions)
    )

    predicted_class = CLASS_NAMES[
        predicted_index
    ]

    confidence = float(
        predictions[predicted_index]
    ) * 100

    probabilities = {

        CLASS_NAMES[i]:
            float(predictions[i]) * 100

        for i in range(
            len(CLASS_NAMES)
        )
    }

    return (
        predicted_class,
        confidence,
        probabilities
    )


# ============================================================
# SEVERITY AND PRIORITY
# ============================================================

def get_severity(
    predicted_class
):

    if predicted_class == "Large pothole":

        return "Major", "High"


    elif predicted_class == "Small pothole":

        return "Minor", "Medium"


    else:

        return "No damage", "None"