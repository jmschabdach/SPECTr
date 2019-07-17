from __future__ import print_function
import numpy as np

# For loading/saving the images
from nipy.core.api import Image
from nipy import load_image, save_image
from nipype.interfaces import dcmstack

class ImageManipulatingLibrary:
    ##
    # Load the image
    #
    # @param fn The string specifying the path to the file
    #
    # @returns img The image sequence as an Image object
    # @returns coords The coordinate system for the image sequence
    def loadBOLD(fn):
        img = load_image(fn)
        coords = img.coordmap

        return img, coords

    ##
    # Isolate a single volume from the sequence
    #
    # @param seq The image sequence as an Image object
    # @param volNum An int specifying the volume to isolate
    #
    # @returns vol The isolated volume
    def isolateVolume(seq, volNum=0):
        # Pull out the volume of interest from the sequence
        vol = seq[:,:,:, volNum].get_data()[:,:,:, None]
        # Make sure that the volume only has 3 dimensions
        if len(vol.shape) == 4:
            vol = np.squeeze(vol)

        return vol

    ##
    # Convert a 4D numpy array to an Image object
    #
    # @param seq The image sequence as a 4D numpy array
    # @param coords The coordinates for the image sequence
    #
    # @returns seqImg The sequence as an Image object
    def convertArrayToImage(seq, coords):
        # Condense the replicated sequence
        seqStack = np.stack(seq, axis=-1)

        # Convert the image sequence into an Image
        seqImg = Image(seqStack, coords)

        return seqImg

    ## 
    # Save the standardized image sequence
    #
    # @param seq The standardized image sequence
    # @param fn The location to save the image sequence to
    def saveBOLD(seq, fn):
        save_image(seq, fn)


def main():
    print("Image Manipulating Library")    

if __name__ == "__main__":
    main()
