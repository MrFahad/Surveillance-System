# import cv2
# from skimage.feature import local_binary_pattern
# import numpy as np

# import face_recognition as fr

# def getFeatures(img):
    
    # encode = np.array(fr.face_encodings(img))
    # encode.drop
    # f2=np.squeeze(encode)
    # return np.squeeze(encode)
    # METHOD = 'uniform'
    # P = 32
    # R = 2
    
    # lbp = local_binary_pattern(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY), P, R, METHOD)
    # n_bins = int(lbp.max() + 1)
    # hist, _ = np.histogram(lbp, normed=True, bins=n_bins, range=(0, n_bins))
    # f1=np.reshape(hist, (np.product(hist.shape),))
    # resized_image = cv2.resize(img, (128, 128))
    # hog = cv2.HOGDescriptor()
    # h = hog.compute(resized_image)
    # f2=np.reshape(h, (np.product(h.shape),))
    # features=np.concatenate((f1,f2))
    # return features

# f1=getFeatures(cv2.imread('data/person/Najeeb/Cam0_2020-03-13_16_43_54_442715.jpg'))
# f2=getFeatures(cv2.imread('data/person/Najeeb/Cam0_2020-03-13_16_44_05_386458.jpg'))
# f1=getFeatures(cv2.cvtColor(cv2.imread('data/person/Nazim/testCam_2020-03-13_15_00_22_343672.jpg'), cv2.COLOR_BGR2GRAY))
# f2=getFeatures(cv2.cvtColor(cv2.imread('data/person/Nazim/testCam_2020-03-13_15_00_19_016008.jpg'), cv2.COLOR_BGR2GRAY))
# print(f1.shape)
# print(f2.shape)
# dist = np.linalg.norm(f1-f2)
# print('distance is',dist)
# from utils import getImagedist


# d=getImagedist('data/temp/Cam0_2020-03-12_17_15_07_782348.jpg','data/temp/Cam0_2020-03-12_17_15_04_100045.jpg')
# print(d)
# import queue

# myq=queue.Queue(5)
# myq.put(1)
# myq.put(2)
# myq.put(3)
# myq.put(4)
# myq.put(5)

# print('my queue',myq.full())


# import cv2
# import os
# import dlib
# from imutils.face_utils import FaceAligner
# from imutils.face_utils import rect_to_bb
# import numpy as np
# mydir='unidentified'
# files=os.listdir(mydir)
# print(files)
# faceDetector    = dlib.get_frontal_face_detector()
# predictor       = dlib.shape_predictor('data/shape_predictor_68_face_landmarks.dat')
# faceAligner     = FaceAligner(predictor, desiredFaceWidth=256)
# count=0
# for f in files:
#     frame=cv2.imread(mydir+'/'+f)
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     cv2.equalizeHist( gray, gray )
#     rects = faceDetector(gray, 1)
#     for rect in rects:
#         (x, y, w, h) = rect_to_bb(rect)
#         faceAligned = faceAligner.align(frame, gray, rect)
#         cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
#         #print(faceAligned.shape)
#         face=np.array(faceAligned[:,26:230,:])
#         # face = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
#         cv2.imwrite('data/person/unknown/'+str(count)+'.jpg',face)
#         count=count+1

# from pony.orm import *
# from Database import mydb
# x=mydb()
# p=(mydb.getAllAttendance())
# for x in p:
#     print(x.datetime)