from boldli import ImageManipulatingLibrary as mil
import numpy as np
from nipype.interfaces.fsl.maths import ApplyMask
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--scan', type=str, help='/path/to/scan/file')
    parser.add_argument('-m', '--mask', type=str, help='/path/to/mask/file')
    parser.add_argument('-o', '--output', type=str, help='/path/to/output/file')

    args = parser.parse_args()

    # Define variables
    sequenceFn = args.scan
    maskFn = args.mask
    outFn = args.output

    # Load the sequence
    sequence, coords1 = mil.loadBOLD(sequenceFn)
    # Load the mask
    mask, coords2 = mil.loadBOLD(maskFn)
    print("sequence", sequence.shape)
    print("mask", mask.shape)

    masking = ApplyMask()
    masking.inputs.in_file = sequenceFn
    masking.inputs.mask_file = maskFn
    masking.inputs.out_file = outFn
    masking.run()

#    # Load the sequence
#    sequence, coords1 = mil.loadBOLD(sequenceFn)
#
#    # If the sequence has a dimension with a size of 1, squeeze it
#    if sequence.shape[-1] == 1:
#        sequence = np.squeeze(sequence)
#    # If the mask has a dimension with a size of 1, squeeze it
#    if mask.shape[-1] == 1:
#        mask = np.squeeze(mask)
#
#    # Set up list of masked volumes
#    maskedSeq = []
#
#    if len(sequence.shape) == 4 and len(mask.shape) == 3:  # Case: 4D sequence and 3D mask
#        # For every volume in the spotted brain image
#        for i in range(sequence.shape[-1]):
#            # Isolate volume
#            volume = mil.isolateVolume(sequence, i)
#            # Apply the mask
#            maskedVol = np.multiply(volume, mask)
#            # Save the masked volume to the list of masked volumes
#            maskedSeq.append(maskedVol)
#    elif len(sequence.shape) == 4 and len(mask.shape) == 4: # Case: 4D sequence and 4D mask
#        # make sure the 4th dimensions are the same length
#        for i in range(sequence.shape[-1]):
#            # Isolate the sequence and mask volumes
#            sequenceVolume = mil.isolateVolume(sequence, i)
#            maskVolume = mil.isolateVolume(mask, i)
#            # Apply the mask
#            maskedVol = np.multiply(sequenceVolume, maskVolume)
#            # Save the masked volume to the list of masked volumes
#            maskedSeq.append(maskedVol)
#    elif len(sequence.shape) == 3 and len(mask.shape) == 3:
#        # Apply the mask
#        maskedVol = np.multiply(sequence, mask)
#        # Save the masked volume to the list of masked volumes
#        maskedSeq = maskedVol # instead of a list, save the single masked volume
#
#    
#    # Save the masked sequence 
#    seqImg = mil.convertArrayToImage(maskedSeq, coords1)
#    mil.saveBOLD(seqImg, outFn) 

if __name__ == "__main__":
    main()
