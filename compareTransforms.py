import argparse
import numpy as np
import scipy.io
import pandas as pd
import math
import os


"""
Calculate the percent error between the two motion matrices

@param matOrig A np array representing the original motion added to the image
@param matExp A np array representing the estimated motion added to the image

@return
"""
def calculatePercentError(matOrig, matExp):
    origRot = matOrig.flatten()
    expRot = matExp.flatten()

    line = ""
    total = 0.0

    for o, e in zip(origRot, expRot):
        # % error = abs(e - o)/o
        if o == e:
            error = 0
        elif o != 0:
            error = abs(e - o)/float(o)
        else: # o == 0
            error = 2*e/(abs(float(e)))
            print(e, o, error)
        total += error
        line += str(error) + ","

    # get translation info
#    line += str(matExp[0,-1])+","+str(matExp[1,-1])+","+str(matExp[2,-1])+","

    line += str(total/float(len(origRot))) + "\n"

    return line


"""
Calculate the L2 norm difference between the two motion matrices

@param matOrig A np array representing the original motion added to the image
@param matExp A np array representing the estimated motion added to the image

@return
"""
def calculateL2(matOrig, matExp):
    origList = matOrig.flatten()
    expList = matExp.flatten()

    # Find the difference between the matrices
    diff = np.array([(o-e) for o, e in zip(origList, expList)])

    # Calculate the L2 norm
    l2 = np.linalg.norm(diff)
    
    return l2



"""
Load data from a .mat file and convert it to a transform matrix

@param fn The name of the file to load

@return mat4 The 4x4 transformation matrix
"""
def loadCalculatedMatrix(fn):
    
    # Load the data from the .mat file
    data = scipy.io.loadmat(fn)
    keys = list(data.keys())

    # Interpret data stored in the .mat file
    array = np.asarray(data[keys[0]])
    mat3 = array[:9].reshape(3, 3)
    translation = array[9:]
    center = np.asarray(data[keys[1]])

    # Use translation and center to calculate offset
    offset = []
    for i in range(len(translation)):
        offset.extend(translation[i] + center[i])
        for j in range(len(translation)):
            offset[i] -= mat3[i][j]*center[j]

    # Combine mat3 and offset to get mat4 (4x4 transformation matrix)
    mat4 = []
    for i in range(len(offset)):
        mat4.append(np.append(mat3[i], offset[i]))

    mat4.append(np.append(np.zeros(len(offset)), 1))
    mat4 = np.asarray(mat4)

    return mat4

"""
Load the .csv file of known motion added to the image sequence.

@param fn The name of the .csv file containing added motion parameters

@returns
"""
def loadAddedMotion(fn):
    # Load the added motion data from the .csv file
    df = pd.read_csv(fn, header=0)
    # Return the data frame
    return df

"""
Convert motion parameters to a transformation matrix

@param xdeg Rotation about the x axis in degrees 
@param ydeg Rotation about the y axis in degrees 
@param zdeg Rotation about the z axis in degrees

@returns mat The 4x4 rotation matrix
"""
def generateKnownMotionMatrix(xdeg, ydeg, zdeg):
    # Convert angles to radians
    xrad = math.radians(-xdeg) 
    yrad = math.radians(-ydeg) 
    zrad = math.radians(-zdeg)

    # Rotation about the z axis
    matrixZ = np.array([[1, 0, 0, 0],
                        [0, np.cos(zrad), -np.sin(zrad), 0],
                        [0, np.sin(zrad), np.cos(zrad), 0],
                        [0, 0, 0, 1]])    

    # Rotation about the x axis
    matrixX = np.array([[np.cos(xrad), 0, np.sin(xrad), 0],
                        [0, 1, 0, 0],
                        [-np.sin(xrad), 0, np.cos(xrad), 0],
                        [0, 0, 0, 1]])

    # Rotation about the y axis
    matrixY = np.array([[np.cos(yrad), -np.sin(yrad), 0, 0],
                        [np.sin(yrad), np.cos(yrad), 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])

    # Composite matrix
    mat = np.dot(np.dot(matrixZ, matrixX), matrixY)
    
    return mat


def main():
    # Set up the argparser
    parser = argparse.ArgumentParser()
    # Add argument for the image sequence name
    parser.add_argument("-i", "--image", help="Image number", type=str)
    # Parse the args
    args = parser.parse_args()

    basePath = "/home/jenna/Research/data/sam/"+args.image+"/"
    transformPath = os.path.join(basePath, "transforms")
#    metricsPath = os.path.join(basePath, "metrics")
    metricsPath = "/home/jenna/Research/data/sam/metrics/"
    if not os.path.exists(metricsPath):
        os.mkdir(metricsPath)

    # Set up the files for the calculated metrics
    l2Fn = os.path.join(metricsPath, "l2norms.csv")
#    if not os.path.exists(l2Fn):
#        with open(l2Fn, "w") as f:
    line = args.image+","


    # Load the dataframe of motion added to the image
    fn2 = os.path.join(basePath, "added_motion.csv")
    xformDf = loadAddedMotion(fn2)
    headers = list(xformDf)
    
    # Get the list of files in the transform directory
    matFiles = [f for f in os.listdir(transformPath) if os.path.isfile(os.path.join(transformPath, f))]
    # For each file
    for f in matFiles:
        # Get the matrix from the .mat file
        cMatrix = loadCalculatedMatrix(os.path.join(transformPath, f))
        # Grab the first 3 characters of the filename (not the base name!)
        sub = int(f[:3])
        # Get the row of the dataframe for that int
        row = xformDf.iloc[sub]
        # Get the transformation matrix for that row
        kMatrix = generateKnownMotionMatrix(float(row[headers[1]]),
                                            float(row[headers[2]]),
                                            float(row[headers[3]]))
        # Compare the two matrices
#        print(calculatePercentError(kMatrix, cMatrix))
        line += str(calculateL2(kMatrix, cMatrix))+","

    line = line[:-1]+"\n"
    with open(l2Fn, "a") as f:
        f.write(line)

if __name__ == "__main__":
    main()
