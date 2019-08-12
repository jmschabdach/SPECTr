import numpy as np
import scipy.io
import pandas as pd

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

    return mat4

"""
Load the .csv file of known motion added to the image sequence.

@param fn The name of the .csv file containing added motion parameters

@returns
"""
def loadAddedMotion(fn):
    # Load the added motion data from the .csv file
    # Print the headers
    # Return the data frame

"""
Convert motion parameters to a transformation matrix

@param

@returns
"""
def generateKnownMotionMatrix():
    pass

def main():
    fn = "/home/jenna/Research/data/sam/1/transforms/001_0Affine.mat"
    
    # Load the calculated transform matrix
    cMatrix = loadCalculatedMatrix(fn)
    print(cMatrix)
    

if __name__ == "__main__":
    main()
