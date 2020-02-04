import argparse
from nipype.interfaces.fsl import BinaryMaths

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--original', type=str, help='Filename of the original image')
    parser.add_argument('-r', '--revised', type=str, help='Filename of the revised image')
    parser.add_argument('-d', '--difference', type=str, help='Filename of the difference image')

    args = parser.parse_args()

    # Calculate the difference between the two images
    differenceImg = BinaryMaths()
    differenceImg.inputs.in_file = args.original
    differenceImg.inputs.operand_file = args.revised
    differenceImg.inputs.operation = 'sub'
    differenceImg.inputs.out_file = args.difference
    differenceImg.run()


if __name__ == "__main__":
    print("alpha")
    main()
