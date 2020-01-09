from boldli import ImageManipulatingLibrary as mil
import numpy as np
import argparse
from nipy.core.api import Image

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sequence', type=str, help='Filename of the sequence to add BOLD signal to')
    parser.add_argument('-r', '--roi', type=str, help='Filename of the ROI image of brain activity')
    parser.add_argument('-o', '--out-fn', type=str, help='Filename to use to save the image with BOLD signal')

    args = parser.parse_args()
    print(args)

    # NOTE: DOES BOLDLI LOAD BOLD RETURN THE IMAGE DATA AND THE COORDS OR JUST THE IMG AND THE COORDS? FIX TO RETURN DATA AND COORDS
    # Load sequence
    seq, seq_coords = mil.loadBOLD(args.sequence)
    # Load ROI
    roi, roi_coords = mil.loadBOLD(args.roi)
    # BOLD signal: f(t) = s*cos(f0*t-delta)+e
    # s: constant, 20% max value
    s = 0.1*np.amax(seq)
    # f0: fundamental frequency, 0.04 Hz
    f0 = 0.04
    # t_shift: temporal shift
    t_shift = 0
    # a_shift: amplitude shift, will be random
    a_shift = 0

    dim1, dim2, dim3 = np.nonzero(roi)

    for i, j, k in zip(dim1, dim2, dim3):
        for t in range(seq.shape[-1]):
            signal = s * np.cos(f0*(t-t_shift)) + a_shift
#            print(signal)
#            print(seq[i][j][k][t])
            seq[i][j][k][t] += signal

    newImg = Image(seq, seq_coords)
    mil.saveBOLD(newImg, args.out_fn)


if __name__ == '__main__':
    main()
