print("---------------------------------------------------")	
print("Implementing Task 2 : Epipolar Geometry")
print("---------------------------------------------------")	
import cv2
import numpy as np
from matplotlib import pyplot as plt
import random
np.random.seed(sum([ord(c) for  c in 'anunayra']))

img1 = cv2.imread('tsucuba_left.png',0)  #queryimage # left image
img2 = cv2.imread('tsucuba_right.png',0) #trainimage # right image

image1 = cv2.imread('tsucuba_left.png')
image2 = cv2.imread('tsucuba_right.png')

sift = cv2.xfeatures2d.SIFT_create()

# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)

im1 = cv2.drawKeypoints(image1, kp1, None)
im2 = cv2.drawKeypoints(image2, kp2, None)
cv2.imwrite("task2_sift1.jpg", im1)
cv2.imwrite("task2_sift2.jpg",im2)

# FLANN parameters
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)

good = []
pts1 = []
pts2 = []

# ratio test as per Lowe's paper
for i,(m,n) in enumerate(matches):
    if m.distance < 0.75*n.distance:
        good.append([m])
        pts2.append(kp2[m.trainIdx].pt)
        pts1.append(kp1[m.queryIdx].pt)

img3 = cv2.drawMatchesKnn(img1,kp1,img2,kp2,good,None,flags=2)
cv2.imwrite("task2_matches_knn.jpg",img3)    

pts1 = np.int32(pts1)
pts2 = np.int32(pts2)
F, mask = cv2.findFundamentalMat(pts1,pts2,cv2.FM_RANSAC)

# We select only inlier points
pts1 = pts1[mask.ravel()==1]
pts2 = pts2[mask.ravel()==1]

def drawlines(img1,img2,lines,pts1,pts2):
    ''' img1 - image on which we draw the epilines for the points in img2
        lines - corresponding epilines '''
    r,c = img1.shape
    img1 = cv2.cvtColor(img1,cv2.COLOR_GRAY2BGR)
    img2 = cv2.cvtColor(img2,cv2.COLOR_GRAY2BGR)
    for r,pt1,pt2 in zip(lines,pts1,pts2):
        color = tuple(np.random.randint(0,255,3).tolist())
        x0,y0 = map(int, [0, -r[2]/r[1] ])
        x1,y1 = map(int, [c, -(r[2]+r[0]*c)/r[1] ])
        img1 = cv2.line(img1, (x0,y0), (x1,y1), color,1)
        img1 = cv2.circle(img1,tuple(pt1),5,color,-1)
        img2 = cv2.circle(img2,tuple(pt2),5,color,-1)
    return img1,img2
    
# Find epilines corresponding to points in right image (second image) and
# drawing its lines on left image
pts1 = np.asarray(random.sample(list(pts1), 10))
pts2 = np.asarray(random.sample(list(pts2), 10))

lines1 = cv2.computeCorrespondEpilines(pts2.reshape(-1,1,2), 2,F)
lines1 = lines1.reshape(-1,3)
img5,img6 = drawlines(img1,img2,lines1,pts1,pts2)

# Find epilines corresponding to points in left image (first image) and
# drawing its lines on right image
lines2 = cv2.computeCorrespondEpilines(pts1.reshape(-1,1,2), 1,F)
lines2 = lines2.reshape(-1,3)
img3,img4 = drawlines(img2,img1,lines2,pts2,pts1)

cv2.imwrite("task2_epi_left.jpg",img5)
print("task2_epi_left.jpg  created...")
cv2.imwrite("task2_epi_right.jpg",img3)
print("task2_epi_right.jpg  created...")
print("---------------------------------------------------")	
print("----------Fundamental Matrix Generated:------------")
print("---------------------------------------------------")	
print(F)
stereo = cv2.StereoBM_create(numDisparities=64, blockSize=13)
disparity = stereo.compute(img1,img2)

plt.imsave("task2_disparity.jpg",disparity)
print("task2_disparity.jpg  created...")