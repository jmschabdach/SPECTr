from __future__ import print_function
import numpy as np
import argparse

# Load custom library
from boldli import ImageManipulatingLibrary as mil

# For loading/saving the images
from nipy.core.api import Image
from nipy import load_image, save_image
from nipype.interfaces import dcmstack

# For manipulating the coordinates
from nipy.core.api import CoordinateSystem, AffineTransform

# For generating the mask
import SimpleITK as sitk

##
# Replicate the volume of interest 150 times
#
# @param vol The image volume
# @param coords The coordinates for the image sequence
#
# @returns newSeq The new image sequence
def replicateVolume(vol):
    # Set up list for image sequence
    newSeq = []

    # Copy the new image into a list
    for i in range(150):
        newSeq.append(np.copy(vol))

    # Return the list of copied volumes
    return newSeq


##
# Generate a 3D volumetric brain mask from the chosen image volume
#
# @param vol The image volume
# 
# @returns mask The image mask
def generateMask(vol):
    # Perform Otsu thresholding
    otsu = sitk.OtsuThresholdImageFilter()
    otsu.SetInsideValue(0)
    otsu.SetOutsideValue(1)
    mask = otsu.Execute(vol)

    return mask

##
# Convert a 3D coordinates object into a 4D coordinates object
#
# @param orig The original coordinates
#
# @returns modified The modified coordinates
def convert3DCoordsTo4D(orig):
    # Get the data from the original coordinates
    domain = orig.function_domain
    outrange = orig.function_range
    affine = orig.affine
    print(type(affine), affine)

    # Add the temporal dimension
    mod_domain = CoordinateSystem(domain.coord_names + ('t',), domain.name, domain.coord_dtype)
    mod_range = CoordinateSystem(outrange.coord_names + ('t',), outrange.name, outrange.coord_dtype)

    # Temporal is a little trickier in the affine matrix
    # Create a new matrix
    mod_affine = np.zeros((5,5))
    # Set up the diagonals
    mod_affine[0, 0] = affine[0,0]
    mod_affine[1, 1] = affine[1,1]
    mod_affine[2, 2] = affine[2,2]
    mod_affine[3, 3] = 2           # This is the new temporal dimension: each volume is 2s apart
    mod_affine[4, 4] = 1           # This is the last row in the matrix and should be all 0 except this column
    # Pull the last column of the first 3 rows into the new matrix
    mod_affine[0, 4] = affine[0, 3]
    mod_affine[1, 4] = affine[1, 3]
    mod_affine[2, 4] = affine[2, 3]

    print(mod_affine)

    modified = AffineTransform(mod_domain, mod_range, mod_affine)
    
    return modified


def main():
    # Future: add arguments for inFn, outFn, and volNum
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='/path/to/input/file')
    parser.add_argument('-o', '--output', type=str, help='/path/to/input/file')
    parser.add_argument('-n', '--volume-number', type=int, help='Which image volume to isolate. If missing, first volume in sequence will be used.')

    args = parser.parse_args()

    # Specify filepaths
    inFn = args.input
    outFn = args.output

    # if the volume number was specified,
    if args.volume_number is not None:
        volNum = args.volume_number
    else:
        volNum = 0

    # Load the original image sequence
    sequence, coordinates = mil.loadBOLD(inFn)

    print(sequence.shape)
    print(coordinates)

    # if the image only has 3 dimensions
    if len(sequence.shape) == 3:
        volume = sequence
        coordinates = convert3DCoordsTo4D(coordinates)
    elif len(sequence.shape) == 4:
        # Isolate the volume of interest
        volume = mil.isolateVolume(sequence, volNum)

    # Replicate the volume
    print("Replicating the volume")
    uniformSeq = replicateVolume(volume)

    # Get a mask of the volume
    print("Creating a mask of the volume")
    volumeImg = sitk.GetImageFromArray(volume)
    mask = generateMask(volumeImg)
    maskArray = sitk.GetArrayFromImage(mask)
    maskStack = mil.convertArrayToImage(np.array([maskArray]), coordinates)
    mil.saveBOLD(maskStack, "generated_brain_mask.nii.gz")

    # Convert the list of replicated volumes into an Image object
    print("Converting the list of replicated volumes to an image")
    seqImg = mil.convertArrayToImage(uniformSeq, coordinates)

    # Save the volume
    print("Saving the image")
    mil.saveBOLD(seqImg, outFn)
    print("Done")
    

if __name__ == "__main__":
    main()
