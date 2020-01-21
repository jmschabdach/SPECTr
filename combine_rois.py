from boldli import ImageManipulatingLibrary as mil
import numpy as np
import argparse
from nipy import save_image, load_image
from nipy.algorithms.resample import resample_img2img
from nipype.interfaces.fsl import BinaryMaths
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-1', '--roi1', type=str, help='Filename of the first ROI image')
    parser.add_argument('-2', '--roi2', type=str, help='Filename of the second ROI image')
    parser.add_argument('-c', '--coord-image', type=str, help='Filename of the coordinates image')
    parser.add_argument('-o', '--output-file', type=str, help='Filename to use for combined ROIs')

    args = parser.parse_args()
    print(args)

    # check that both images exist
    if not os.path.exists(args.roi1):
        print("File '"+args.roi1+"' does not exist")
    if not os.path.exists(args.roi2):
        print("File '"+args.roi2+"' does not exist")
    if not os.path.exists(args.coord_image):
        print("File '"+args.coord_image)

    # load both images for the purpose of checking coordinates
    roi1, coords1 = mil.loadBOLD(args.roi1)
    roi2, coords2 = mil.loadBOLD(args.roi2)
    img, imgCoords = mil.loadBOLD(args.coord_image)

    print("roi1", roi1.shape)
    print("roi2", roi2.shape)
    print("coords", img.shape)

    # perform the OR-ing of the 2 rois
    addingImgs = BinaryMaths()
    addingImgs.inputs.in_file = args.roi1
    addingImgs.inputs.operand_file = args.roi2
    addingImgs.inputs.operation = "max"
    addingImgs.inputs.out_file = args.output_file
    addingImgs.run()

    # resample the new roi to be in the coordinate frame of the coordinate image
    jointRoi = load_image(args.output_file)
    coordsImg = load_image(args.coord_image)
    print("joint rois", jointRoi.get_data().shape)
    newRoiImg = resample_img2img(jointRoi, coordsImg, order=0)
    save_image(newRoiImg, args.output_file)

    # create combo image
#    combinedRoi = np.add(roi1, roi2)

#    # Resize the combo image
#    newImgArray = np.zeros(img.shape)
#    i_coords, j_coords, k_coords = np.nonzero(combinedRoi)
#
#    # New affine transform
#    affine_old_to_new = np.matmul(np.linalg.inv(imgCoords.affine), coords1.affine)
#
#    for i, j, k in zip(i_coords, j_coords, k_coords):
#        # Find new coordinates
#        vec_old = np.array([[i, j, k, 1]]).T
#        vec_mid = np.matmul(affine_old_to_new, vec_old)
#        vec_new = [int(m) for m in vec_mid]
#
#        # Include the surrounding positions
#        #    1 -> 1 0 -> 1 1
#        #         0 0    1 1
#        for m in [vec_new[0], vec_new[0]+1]:
#            for n in [vec_new[1], vec_new[1]+1]:
#                for p in [vec_new[2], vec_new[2]+1]:
#                    if m < img.shape[0] and n < img.shape[1] and p < img.shape[2]:
#                        newImgArray[m][n][p] = 1
#                    else:
#                        print(vec_old.T, vec_new)
#
#    # save combo image
#    combinedRoiImg = mil.convertArrayToImage(newImgArray, imgCoords)
#    mil.saveBOLD(combinedRoiImg, args.output_file)


if __name__ == '__main__':
    main()

