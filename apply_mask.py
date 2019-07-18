from boldli import ImageManipulatingLibrary as mil
import numpy as np

def main():
    # Define variables
    sequenceFn = ""
    maskFn = "brain_mask.nii.gz"
    outFn = "brain_spotty_maks.nii.gz"

    # Load the spotted brain image
    sequence, coords1 = mil.loadBOLD(sequenceFn)
    # Load the brain mask
    mask, coords2 = mil.loadBOLD(maskFn)
    mask = np.squeeze(mask)

    # Set up list of masked volumes
    maskedSeq = []

    # For every volume in the spotted brain image
    for i in range(sequence.shape[-1]):
        # Isolate volume
        volume = mil.isolateVolume(sequence, i)
        # Apply the mask
        maskedVol = np.multiply(volume, mask)
        # Save the masked volume to the list of masked volumes
        maskedSeq.append(maskedVol)

    # Save the masked sequence
    seqImg = mil.convertArrayToImage(maskedSeq, coords1)
    mil.saveBOLD(seqImg, outFn) 
    

if __name__ == "__main__":
    main()
