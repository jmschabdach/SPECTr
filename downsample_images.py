from __future__ import print_function
import argparse

import nibabel
import nibabel.processing

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

    # resample the image
    resampled = nibabel.processing.resample_to_output(img, [4,4,4])

    # Save the volume
    nibabel.save(resampled, outFn)
    

if __name__ == "__main__":
    main()
