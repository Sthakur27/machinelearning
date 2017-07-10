from __future__ import print_function
import keras
from keras.datasets import mnist
from keras import backend as K
from keras.models import load_model
import numpy as np
def mypredict(x):
    mymodel=load_model('conv_classifier.h5')
    #return(1)
    arr=mymodel.predict(x,batch_size=1,verbose=1)[0]
    maxVal=0
    maxIndex=0
    for i in range(0,len(arr)):
        if(arr[i]>maxVal):
            maxVal=arr[i]
            maxIndex=i
    return(maxIndex)

def datatest():
    # input image dimensions
    img_rows, img_cols = 28, 28
    # the data, shuffled and split between train and test sets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
    
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    idx=300
    testpic=x_train[idx]
    for y in reversed(range(0,len(testpic[0]))):
        for x in range(0,len(testpic)):
            if(testpic[x][y][0]<0.5):
                print("X", end=" ")
            else:
                print(" ", end=" ")
            #print(testpic[x][y], end=" ")
        print("")
    print(mypredict(np.array([x_train[idx]])))
    print("Should be %s"%y_train[idx])

def runtestsagain():
    # input image dimensions
    img_rows, img_cols = 28, 28
    num_classes=10
    # the data, shuffled and split between train and test sets
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    if K.image_data_format() == 'channels_first':
        x_train = x_train.reshape(x_train.shape[0], 1, img_rows, img_cols)
        x_test = x_test.reshape(x_test.shape[0], 1, img_rows, img_cols)
        input_shape = (1, img_rows, img_cols)
    else:
        x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1)
        x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1)
        input_shape = (img_rows, img_cols, 1)
    
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    x_train /= 255
    x_test /= 255
    # convert class vectors to binary class matrices
    y_train = keras.utils.to_categorical(y_train, num_classes)
    y_test = keras.utils.to_categorical(y_test, num_classes)
    print('x_train shape:', x_train.shape)
    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    mymodel=load_model('conv_classifier.h5')
    score = mymodel.evaluate(x_test, y_test, verbose=0)
    print('Test accuracy:', score[1])

#datatest() 