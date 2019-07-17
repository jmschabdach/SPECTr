import numpy as np
import matplotlib.pyplot as plt
import cv2                         # Installed in opencv

# For loading/saving the images
from nipy.core.api import Image
from nipy import load_image, save_image
from nipype.interfaces import dcmstack

# Import custom library
from boldli import ImageManipulatingLibrary as mil

##
# Generate a single 3D Gaussian distribution at a 
# specific location in the image
#
# @param img The image as a numpy array
# @param x The x coordinate for the center of the distribution
# @param y The y coordinate for the center of the distribution
# @param z The z coordinate for the center of the distribution
# @param diameter Int value specifying the diameter of the distribution in pixels
# @param intensity Float value to scale the intensity of the distribution
#
# @returns newImg The distribution located at (x, y, z) in a blank image
def generateBlur(img, x, y, z, diameter=50, intensity=1.0):

    # Generate the 3D Gaussian distribution 
    gridX, gridY, gridZ = np.meshgrid(np.linspace(-1,1,diameter), 
                                      np.linspace(-1,1,diameter),
                                      np.linspace(-1,1,diameter))

    grid = np.sqrt(gridX*gridX+gridY*gridY+gridZ*gridZ)
    sigma = .5
    blur = intensity * np.exp(-((grid)**2/(2.0*sigma**2)))

    # Make sure that the values of blur are int values
    blur = np.around(blur)

    # Set up int values for zero padding
    lpad = int(np.floor(x - (diameter/2.0)))
    rpad = int(np.ceil(img.shape[2] - lpad - diameter))
    upad = int(np.floor(y - (diameter/2.0)))
    spad = int(np.floor(z - (diameter/2.0)))

    # Create a blank, image sized canvas
    newImg = np.zeros(img.shape)

    # Pad the distribution
    for sliceIdx in range(len(blur)):
        for row in range(len(blur[sliceIdx])):
            newImg[sliceIdx+spad, row+upad] = np.pad(blur[sliceIdx, row], (lpad, rpad), 
                                                     'constant', constant_values=(0.0, 0.0))

    return newImg

##
# Additively combine 2 images
#
# @param img1 The first image
# @param img2 The second image
#
# @returns newImg The combination of img1 and img2
def addImages(img1, img2):
    newImg = np.add(img1, img2)
    return newImg


##
# Generate random points for the blurs
#
# @param

def main():
    # Specify the name of the file to load
    inFn = "standard.nii.gz"
    spotsFn = "spots.nii.gz"
    outFn = "standard_with_BOLD.nii.gz"

    # Load the file
    sequence, coordinates = mil.loadBOLD(inFn)
    print("Image loaded.")

    spotsList = []
    brainSpotsList = []

    # For each volume in the sequence
    for idx in range(sequence.shape[-1]):
        # Isolate a single image volume
        vol = mil.isolateVolume(sequence, volNum=idx)

        # Future: randomize/automate this
        # Generate some 3D Gaussian distributions
        spot1 = generateBlur(vol, 15, 10, 10, diameter=5, intensity=1000)
        spot2 = generateBlur(vol, 23, 40, 20, diameter=5, intensity=1000)
        spot3 = generateBlur(vol, 7, 38, 17, diameter=5, intensity=1000)

        # Combine all of the spots to a single image
        allSpots = addImages(spot1, spot2)
        allSpots = addImages(allSpots, spot3)
        spotsList.append(allSpots)

        # Add the spots to the loaded image
        brainSpots = addImages(allSpots, vol)
        brainSpotsList.append(brainSpots)


    # Save the brain image with spots in it
    brainSpots = mil.convertArrayToImage(brainSpotsList, coordinates)
    mil.saveBOLD(brainSpots, outFn)

    # Save the spots image
    allSpots = mil.convertArrayToImage(spotsList, coordinates)
    mil.saveBOLD(allSpots, spotsFn)

if __name__ == "__main__":
    main()
