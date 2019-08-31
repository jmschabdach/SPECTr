import SimpleITK as sitk
import numpy as np
import argparse

##
# Generate a set of points to use to test the distance between the transforms
# 
# @param k The number of points to generate
#
# @return points A list of k points represented in 3D Cartesian space
def generatePoints(k=10):
    points = [tuple(np.random.uniform(size=3)) for i in range(k)]
    return points

##
# Load transformation as sitk.AffineTransform
#
# @param fn The location of the file to load as a string
#
# @return xform The loaded sitk.AffineTransform object
def loadTransform(fn):
    xform = sitk.ReadTransform(fn)
    return xform

##
# Compare pair of transforms using the norm of the difference between the transformed points
#
# @param f1 A string for a file containing sitk.AffineTransform object
# @param f2 A string for a file containing sitk.AffineTransform object
# @param points List of points (tuples) for comparing transforms
#
# @return norms List of norms of the differences between two points
def compareTwoTransforms(f1, f2, points):
    # Load the transforms
    t1 = loadTransform(f1)
    t2 = loadTransform(f2)

    # Make a list for the calculated norms
    norms = []
    # For each point in the list of points,
    for pt in points:
        # Calculate the norm (default Frobenius) of the difference of the transformed points
        norm = np.linalg.norm(t1.TransformPoint(pt) - t2.TransformPoint(pt))
        # Add the norm to the list of norms
        norms.append(norm)

    # Returns the list of norms
    return norms

##
# Compare generated and calculated motion for a single sequence
def compareAllMotion():
    # generate test points
    points = generatePoints()
    # save test points

    # for each timepoint in the calculated motion (generated motion has +1 length)
    
    # compare the two transforms
    # store the difference between the transforms in a list of lists
    # return the list of lists of norms
    pass 

def main():
    # Testing
    generatePoints()
    # Argparser set up
    # Add arg for generated transform directory
    # Add arg for calculated transform directory
    # Parse args
    # Compare all motion in the generated and calculated directories
    # Save the list of lists of norms to a file
    # Calculate the mean and standard deviation of the norms
    # Display the mean and standard deviation of the norms to the user


if __name__ == "__main__":
    main()
