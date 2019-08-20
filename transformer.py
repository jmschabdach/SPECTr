import SimpleITK as sitk
import numpy as np
import math
import argparse
from boldli import ImageManipulatingLibrary as mil

##
# Rotate the image a specific number of degrees about a specific axis
#
# @param point Point in Cartesian coordinates to rotate
# @param deg Float representation of degrees
# @param ax The axis to rotate about. Currently set to X = 0, Y = 1, Z = 2
# 
# @returns rotateTransform An sitk.AffineTransform with a rotation about one axis
def generateRotationTransform(dim, deg, ax, center):
    # Convert the angle from degrees to radians
    rad = math.radians(-deg)
    # Set up the new Affine Transform
    rotateTransform = sitk.AffineTransform(dim)

    # Set the rotation matrix depending on the axis of rotation
    if ax == 0:
        # Rotation about the z axis
        matrix = np.array([[1, 0, 0],
                           [0, np.cos(rad), -np.sin(rad)],
                           [0, np.sin(rad), np.cos(rad)]])
    elif ax == 1:
        # Rotation about the x axis
        matrix = np.array([[np.cos(rad), 0, np.sin(rad)],
                           [0, 1, 0],
                           [-np.sin(rad), 0, np.cos(rad)]])

    elif ax == 2:
        # Rotation about the y axis
        matrix = np.array([[np.cos(rad), -np.sin(rad), 0],
                           [np.sin(rad), np.cos(rad), 0],
                           [0, 0, 1]])
  
    else:
        # raise an error, this shouldn't happen
        print("Error: invalid axis of rotation")
        exit(-1)

    rotateTransform.SetMatrix(matrix.ravel())

    # Set the point at which the transform should be applied
    rotateTransform.SetCenter(center)
    print(center)
 
    return rotateTransform


##
# Generate a scaling transform
#
# @param dim Int number of dimensions
# @param scale Float scaling factor
#
# @returns scaleTransform A sitk.AffineTransform object
def generateScaleTransform(dim, scale):
    # Set up the new Affine Transform
    scaleTransform = sitk.AffineTransform(dim)
    # Make the matrix containing the scaling factors
    scalingMatrix = np.zeros((dim, dim))
    for i in range(dim):
        scalingMatrix[i, i] = scale

    scaleTransform.SetMatrix(scalingMatrix.ravel())

    return scaleTransform

## 
# Generate translation transform
#
# @param dim Int number of dimensions
# @param shift List of shifts in the format [tx, ty, tz]
#
# @returns shiftTransform A sitk.AffineTransform object
def generateShiftTransform(dim, shift, center):
    # Set up the new Affine Transform
    shiftTransform = sitk.AffineTransform(dim)
    # Set the translation parameter
    shiftTransform.SetTranslation((shift[0], shift[1], shift[2]))
    # Set the point at which the transform should be applied
    shiftTransform.SetCenter(center)
    
    return shiftTransform


##
# Perform a transformation and any necessary interpolation on an image volume
#
# @param volume The image volume to be transformed
# @param transform The sitk transform to apply
#
# @returns transformed The transformed image volume
def performTransform(volume, transform):
    interp = sitk.sitkNearestNeighbor
    missing = 0
    transformed = sitk.Resample(volume, transform, interp, missing)

    return transformed

## 
# Check reasonableness of angles being sent to the rotation transform generator
#
# @param xdeg Degrees of rotation about the x axis
# @param ydeg Degrees of rotation about the y axis
# @param zdeg Degrees of rotation about the z axis
#
# @returns reasonableAngles A list of reasonable rotations
def sanityCheckRotation(xdeg, ydeg, zdeg):
    # Current reasonable criteria:
    #   -30 <= x <= 30
    #   -20 <= y <= 45
    #   -75 <= z <= 75
    xUpper = 30
    xLower = -30
    yUpper = 45
    yLower = -20
    zUpper = 75
    zLower = -75

    # Check x
    if xdeg < xLower:
        xdeg = xLower
    elif xdeg > xUpper:
        xdeg = xUpper

    # Check y
    if ydeg < yLower:
        ydeg = yLower
    elif ydeg > yUpper:
        ydeg = yUpper

    # Check z
    if zdeg < zLower:
        zdeg = zLower
    elif zdeg > zUpper:
        zdeg = zUpper

    return xdeg, ydeg, zdeg

##
# Pick a value from a normal distribution to use to adjust a transform parameter
#
# @param mean Float mean of the distribution (center)
# @param std Float standard deviation of the distribution (width)
#
# @returns change The amount to change a transform parameter by
def delta(mean=0.0, std=1.0):
    change = np.random.normal(mean, std)
    return change

##
# Write a line to a file
#
# @param fn String representing the filename
# @param line The line to write as a string
def updateFile(fn, line):
    # Add a newline character if line does not end with one
    if not line.endswith("\n"):
        line = line + "\n"

    # Write the line to the file
    with open(fn, "a+") as f:
        f.write(line)


def main():
    # Set up the argument parser
    #parser = argparse.ArgumentParserl(description="Add motion to a BOLD image.")
    # Add argument: input file name
    #parser.add_argument("-i", "--input", type=str, help="Path to input file")
    # Add argument: output file name
    #parser.add_argument("-o", "--output", type=str, help="Path to output file")


    # Specify variables
    inFn = "BOLD.nii.gz"
    outFn = "moving_brain.nii.gz"
    logFn = "motion_variables.csv"

    # Set up log file header
    header = "Volume Number, X Angle, Y Angle, Z Angle\n"
    updateFile(logFn, header)

    # Load image
    seq, coords = mil.loadBOLD(inFn)

    # Make list for storing volumes of new image
    newSeq = []

    # Assume no rotations in the initial image
    xAngle = 0.0
    yAngle = 0.0
    zAngle = 0.0

    # Calculate offset for center of brain - this is the correct allocation of dimensions
    offset = [seq.shape[2]/2.,
              seq.shape[0]/2.,
              seq.shape[1]/2.]  

    # For every volume in the sequence
    for i in range(seq.shape[-1]):

        print("Volume:", i)

        # Isolate image volume
        vol = mil.isolateVolume(seq, i)
        dimensions = vol.shape
        vol = sitk.GetImageFromArray(vol)

        # Write the angles for the current transformation to the log file
        line = str(i)+", "+str(xAngle)+", "+str(yAngle)+", "+str(zAngle)
        updateFile(logFn, line)

        # Perform rotations
        # ...about the z axis
        zrotate = generateRotationTransform(len(dimensions), zAngle, 0, offset)
        volRotated = performTransform(vol, zrotate)
        zAngle = zAngle + delta()

        # ...about the y axis
        yrotate = generateRotationTransform(len(dimensions), yAngle, 0, offset)
        volRotated = performTransform(volRotated, yrotate)
        yAngle = yAngle + delta()

        # ...about the x axis
        xrotate = generateRotationTransform(len(dimensions), xAngle, 0, offset)
        volRotated = performTransform(volRotated, xrotate)
        xAngle = xAngle + delta()

        # Check the new angles for the next image volume
        xAngle, yAngle, zAngle = sanityCheckRotation(xAngle, yAngle, zAngle)
       
        # Convert the Image to an array so we can work with it
        volNew = sitk.GetArrayFromImage(volRotated)

        # Add new image volume to sequence
        newSeq.append(volNew)

    # Convert the list of transformed image volumes into a BOLD sequence
    newBOLD = mil.convertArrayToImage(newSeq, coords)
    # Save the transformed BOLD sequence
    mil.saveBOLD(newBOLD, outFn)


if __name__ == "__main__":
    main()
