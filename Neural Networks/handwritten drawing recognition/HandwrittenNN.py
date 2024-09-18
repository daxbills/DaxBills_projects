import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
from PIL import Image

def load_and_preprocess_image(image_path):
    img = Image.open(image_path).convert('L')
    img = img.resize((28, 28))
    img_array = np.array(img)
    img_array = tf.keras.utils.normalize(img_array, axis=1)
    img_array = img_array.reshape(1, 28, 28)
    return img_array

mnist=tf.keras.datasets.mnist
(x_train,y_train),(x_test,y_test)=mnist.load_data()


x_train - tf.keras.utils.normalize(x_train, axis=1)
x_test = tf.keras.utils.normalize(x_test, axis=1)
nnmodel = tf.keras.models.Sequential()

nnmodel.add(tf.keras.layers.Flatten(input_shape=(28,28)))
nnmodel.add(tf.keras.layers.Dense(128, activation='sigmoid'))
nnmodel.add(tf.keras.layers.Dense(128, activation='sigmoid'))
nnmodel.add(tf.keras.layers.Dense(10, activation='softmax'))
nnmodel.compile(optimizer='adam',loss='sparse_categorical_crossentropy', metrics=['accuracy'])
nnmodel.fit(x_train,y_train, epochs=8)

loss, accuracy, = nnmodel.evaluate(x_test,y_test)
print(loss)
print(accuracy)
image=8
image_path = 'Neural Networks\handwritten drawing recognition\8.png'
custom_image = load_and_preprocess_image(image_path)
prediction = nnmodel.predict(custom_image)
print("Prediction:", np.argmax(prediction))
if image == np.argmax(prediction):
    print('Prediction is correct')
else:
    print("Prediction is incorrect")
