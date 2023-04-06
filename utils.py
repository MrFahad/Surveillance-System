import cv2
from skimage.feature import local_binary_pattern
import numpy as np
import face_recognition as fr
def getFeatures(img):
    
    encode = np.array(fr.face_encodings(img))
    f2=np.squeeze(encode)
    if f2.shape[0] == 0:
        return None
    METHOD = 'uniform'
    P = 32
    R = 2
    lbp = local_binary_pattern(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), P, R, METHOD)
    n_bins = int(lbp.max() + 1)
    hist, _ = np.histogram(lbp, normed=True, bins=n_bins, range=(0, n_bins))
    f1=np.reshape(hist, (np.product(hist.shape),))
    # print('f1 shape',f1.shape)
    features=np.concatenate((f1,f2))
    return features
def getDistance(f1,f2):
    
    return np.linalg.norm(f1-f2)
def getImagedist(img1,img2):
    # f1=getFeatures(cv2.cvtColor(cv2.imread(img1), cv2.COLOR_BGR2GRAY))
    # f2=getFeatures(cv2.cvtColor(cv2.imread(img2), cv2.COLOR_BGR2GRAY))
    f1=getFeatures(img1)#cv2.imread(img1))
    f2=getFeatures(img1)#cv2.imread(img2))
    if f1.shape == f2.shape:
        return getDistance(f1,f2)
    else:
        return 1