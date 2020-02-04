import SimpleITK as sitk
import numpy as np
import math
import os
import argparse
from boldli import ImageManipulatingLibrary as mil

from skimage.measure import regionprops

##
# Calculate the center of mass for the image
#
# @param vol The image volume
#
# @returns com Center of mass as a list
def calculateCOM(vol):
    # Threshold the data
    labeled = (vol > 0).astype(int)
    # Calculate the properties of the data
    properties = regionprops(labeled, vol)
    # Get the centroid
    centroid = properties[0].centroid
    # Round to get the center of mass invoxels
    com = [int(round(i)) for i in centroid]

    return com

##
# Generate an affine transformation with rotation and translation
#
# @param xdeg Degrees of rotation about the image's x axis
# @param ydeg Degrees of rotation about the image's y axis
# @param zdeg Degrees of rotation about the image's z axis
# @param translation Tuple of 3 points specifying the translation to apply
# @param center Tuple of 3 points specifying the center of the image
# 
# @returns transform An sitk.AffineTransform with rotation and translation components
def generateAffineTransform(xdeg, ydeg, zdeg, translation, center):
    # Convert the angle from degrees to radians
    xrad = math.radians(-xdeg)
    yrad = math.radians(-ydeg)
    zrad = math.radians(-zdeg)
    # Set up the new Affine Transform
    transform = sitk.AffineTransform(3)

    # Generate the rotation matrices 
    # Rotation about the z axis
    zmatrix = np.array([[1, 0, 0],
                        [0, np.cos(zrad), -np.sin(zrad)],
                        [0, np.sin(zrad), np.cos(zrad)]])

    # Rotation about the x axis
    xmatrix = np.array([[np.cos(xrad), 0, np.sin(xrad)],
                       [0, 1, 0],
                       [-np.sin(xrad), 0, np.cos(xrad)]])

    # Rotation about the y axis
    ymatrix = np.array([[np.cos(yrad), -np.sin(yrad), 0],
                       [np.sin(yrad), np.cos(yrad), 0],
                       [0, 0, 1]])

    # Multiply the matrices together 
    matrix = zmatrix.dot(xmatrix.dot(ymatrix))

    # Set the rotation aspect of the transform
    transform.SetMatrix(matrix.ravel())

    # Set the translation aspect of the transform
    transform.SetTranslation(translation)

    # Set the point at which the transform should be applied
    transform.SetCenter(center)
 
    return transform


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
# Save an affine transformation to a file
#
# @param transform An sitk.AffineTransform object
# @param fn Name of the file to save the transform to as a string
def saveTransformInfo(transform, fn):
    sitk.WriteTransform(transform, fn)


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
    parser = argparse.ArgumentParser(description="Add motion to a BOLD image.")
    # Add argument: input file name
    parser.add_argument("-i", "--input", type=str, help="Path to input file")
    # Add argument: output file name
    parser.add_argument("-o", "--output", type=str, help="Path to output file")

    # Parse the arguments
    args = parser.parse_args()
    print(args)

    # Specify variables
    inFn = args.input
    baseDir = os.path.dirname(inFn)
    transformDir = os.path.join(baseDir, "generated_transforms")
    if not os.path.exists(transformDir):
        os.mkdir(transformDir)
    #outFn = os.path.join(baseDir, "moving_brain.nii.gz")
    outFn = args.output
    logFn = os.path.join(baseDir, "motion_variables.csv")

    # Set up log file header
    header = "Volume Number, X Angle, Y Angle, Z Angle, X Translation, Y Translation, Z Translation\n"
    updateFile(logFn, header)
    
    print("Loading the image")
    # Load image
    seq, coords = mil.loadBOLD(inFn)

    # Make list for storing volumes of new image
    newSeq = []

    # Assume no motion in the initial image
    xAngle = 0.0
    yAngle = 0.0
    zAngle = 0.0
    xShift = 0.0
    yShift = 0.0
    zShift = 0.0

    # For every volume in the sequence
    for i in range(seq.shape[-1]):

        print("Volume:", i)

        # Isolate image volume
        vol = mil.isolateVolume(seq, i)

        # Calculate the center of mass
        offset = calculateCOM(vol)

        dimensions = vol.shape
        vol = sitk.GetImageFromArray(vol)

        # Write the angles for the current transformation to the log file
        line = str(i)+", "+str(xAngle)+", "+str(yAngle)+", "+str(zAngle)+", "+str(xShift)+", "+str(yShift)+", "+str(zShift)
        updateFile(logFn, line)

            # Generate transformation
        transform = generateAffineTransform(xAngle, yAngle, zAngle, (xShift, yShift, zShift), offset)
       
        # Apply transformation to image
        volTransformed = performTransform(vol, transform)

        # Save the transformation
        fn = os.path.join(transformDir, str(i).zfill(3)+"_generated_Affine.mat")
        saveTransformInfo(transform, fn)

        # Convert the Image to an array so we can work with it
        volNew = sitk.GetArrayFromImage(volTransformed)

        # Add new image volume to sequence
        newSeq.append(volNew)

        # Update angles
        zAngle = zAngle + delta()
        yAngle = yAngle + delta()
        xAngle = xAngle + delta()

        # Check the new angles for the next image volume
        xAngle, yAngle, zAngle = sanityCheckRotation(xAngle, yAngle, zAngle)
 
        # Update translations
#        zShift = zShift + delta()
#        yShift = yShift + delta()
#        xShift = xShift + delta()

        # Check the new translations for the next image volume
        # UNDER DEVELOPMENT

    # Convert the list of transformed image volumes into a BOLD sequence
    newBOLD = mil.convertArrayToImage(newSeq, coords)
    # Save the transformed BOLD sequence
    mil.saveBOLD(newBOLD, outFn)


if __name__ == "__main__":
    main()
