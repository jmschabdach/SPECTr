from __future__ import print_function
import numpy as np

# Load custom library
from boldli import ImageManipulatingLibrary as mil

# For loading/saving the images
from nipy.core.api import Image
from nipy import load_image, save_image
from nipype.interfaces import dcmstack

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


def main():
    # Future: add arguments for inFn, outFn, and volNum

    # Specify filepaths
    inFn = "BOLD.nii.gz"
    outFn = "standard.nii.gz"

    # Load the original image sequence
    sequence, coordinates = mil.loadBOLD(inFn)

    # Isolate the volume of interest
    volume = mil.isolateVolume(sequence)

    # Replicate the volume
    uniformSeq = replicateVolume(volume)

    # Convert the list of replicated volumes into an Image object
    seqImg = mil.convertArrayToImage(uniformSeq, coordinates)

    # Save the volume
    mil.saveBOLD(seqImg, outFn)
    

if __name__ == "__main__":
    main()
