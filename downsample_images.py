from __future__ import print_function
import argparse

import nibabel
import nibabel.processing
from nilearn.image import math_img
import numpy as np
from boldli import ImageManipulatingLibrary as mil
from nipy.core.api import CoordinateSystem, AffineTransform

def changeCoords2(affine, scale, coords):
    domain = coords.function_domain
    outrange = coords.function_range

    # Create a new matrix
    mod_affine = np.zeros((4,4))
    # Set up the diagonals
    mod_affine[0, 0] = affine[0,0] * scale
    mod_affine[1, 1] = affine[1,1] * scale
    mod_affine[2, 2] = affine[2,2] * scale
    mod_affine[3, 3] = 1           # This is the new temporal dimension: each vol    ume is 2s apart
    # Pull the last column of the first 3 rows into the new matrix
    mod_affine[0, 3] = affine[0, 3] // scale 
    mod_affine[1, 3] = affine[1, 3] // scale
    mod_affine[2, 3] = affine[2, 3] // scale 

    modified = AffineTransform(domain, outrange, mod_affine)

    return modified


def changeCoords(affine, scale):
    # Create a new matrix
    mod_affine = np.zeros((4,4))
    # Set up the diagonals
    mod_affine[0, 0] = affine[0,0] * scale
    mod_affine[1, 1] = affine[1,1] * scale
    mod_affine[2, 2] = affine[2,2] * scale
    mod_affine[3, 3] = 1     
    # Pull the last column of the first 3 rows into the new matrix
    mod_affine[0, 3] = affine[0, 3] // scale 
    mod_affine[1, 3] = affine[1, 3] // scale
    mod_affine[2, 3] = affine[2, 3] // scale 

    return mod_affine

def main():
    # Future: add arguments for inFn, outFn, and volNum
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='/path/to/input/file')
    parser.add_argument('-o', '--output', type=str, help='/path/to/input/file')

    args = parser.parse_args()

    # Specify filepaths
    inFn = args.input
    outFn = args.output

    # load the image
    img = nibabel.load(inFn)
    aff = img.affine

    # resample the image
    resampled = nibabel.processing.resample_to_output(img, [4,4,4])

    scaling = np.abs(4 / aff[0][0])

    # If the image was a mask, threshold it to a binary image
    if "mask" in inFn:
        resampled = math_img("img >= 1", img=resampled)

#     newAff = changeCoords(aff, scaling)
#     print(aff)
#     print(newAff)
#     data = resampled.get_fdata()
#     img = nibabel.Nifti1Image(data, newAff)

    # Save the volume
#    nibabel.save(img, outFn)
    nibabel.save(resampled, outFn)

#     # Load the volume
#     _, coords = mil.loadBOLD(inFn)
#     
#     # Resample coordinates
#     newCoords = changeCoords(aff, scaling, coords)
#     print(newCoords)
#     newImg = mil.convertArrayToImage(data, newCoords)
#     mil.saveBOLD(newImg, outFn)

if __name__ == "__main__":
    main()
