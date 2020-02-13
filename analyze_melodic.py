import argparse
from nipy import load_image, save_image
import numpy as np
import argparse

def main():
    # set up argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-r", "--roi-fn", type=str)
    # parse the args

    args = parser.parse_args()
    melodicFn = args.input
    roiFn = args.roi_fn
#    melodicFn = "./testing_melodic/melodic_IC.nii.gz"
#    roiFn = "./sandbox/dmn_roi.nii.gz"

    # load the images
    melodic = load_image(melodicFn)
    melodicData = melodic.get_data()
    melodicCoords = melodic.coordmap
    roi = load_image(roiFn)
    roiData = roi.get_data()
    roiCoords = roi.coordmap

    print(roiData.shape)
    if len(roiData.shape) == 4:
        roiData = np.average(roiData, axis=-1)

    maxCorr = 0.0
    maxCorrVol = 0
    correlations = []
    vols = []

    # Threshold the rois
    melodicData = np.abs(melodicData)
    melodicData[melodicData > 0.0 ] = 1
    melodicData[melodicData <= 0.0 ] = 0
    
    # for each volume in melodicData
    for i in range(melodicData.shape[-1]):
        # calculate the correlation with the roiData
        corr = np.correlate(melodicData[:, :, :, i].flatten(), roiData.flatten())
        correlations.append(corr[0])
        vols.append(i)
        # if the calculated correlation > max correlation
        if corr > maxCorr:
            # max correlation = calculated correlation
            maxCorr = corr
            # max corr volume = current volume number
            maxCorrVol = i+1

    # sort the correlations and volume numbers
    sortCorrVols = sorted(zip(correlations, vols))

    # print results summary
    print("MELODIC extracted", melodicData.shape[-1], "components.")
    print("      Max correlation to DMN ROI:", maxCorr)
    print("  Component with max correlation:", maxCorrVol)
    print(".")
    print("Best correlations and their components:")
    for i in range(len(sortCorrVols)):
        print(sortCorrVols[i])

if __name__ == "__main__":
    main()
