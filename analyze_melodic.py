import argparse
from nipy import load_image, save_image
import numpy as np
import argparse
import os
from skimage import filters

def calculateRates(roi, component):

    tp = 0
    fp = 0
    tn = 0
    fn = 0
    
    print(roi.shape == component.shape)
    
    for gt, c in zip(roi.flatten(), component.flatten()):
        if gt==c==True:
            tp+= 1
        if gt==c==False:
            tn+=1
        if gt==True and c==False:
            fn+=1
        if gt==False and c==True:
            fp+=1

    tpr = tp/float(tp+fn)
    fnr = fn/float(tp+fn)
    fpr = fp/float(tn+fp)
    tnr = tn/float(tn+fp)

    return tpr, fpr, tnr, fnr

def main():
    # set up argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--input_dir", type=str)
    parser.add_argument("-r", "--roi-fn", type=str)
    parser.add_argument("-t", "--regtype", type=str)

    # parse the args
    args = parser.parse_args()
    subjDir = args.input_dir
    roiFn = args.roi_fn
    regtype = args.regtype
    
    # Set up the file names
    melodicFn = subjDir+regtype+"_melodic/melodic_IC.nii.gz"
    correctedFn = subjDir+"corrected_"+regtype+".nii.gz"
    stationaryFn = subjDir+"BOLD.nii.gz"
    outFn = subjDir+regtype+"_components_correlations.csv"
    overviewFn = "spectr_recovered_components.csv"

    # load the images
    melodic = load_image(melodicFn)
    melodicData = melodic.get_data()
    melodicCoords = melodic.coordmap
    roi = load_image(roiFn)
    roiData = roi.get_data()
    roiCoords = roi.coordmap
    corrected = load_image(correctedFn)
    corrData = corrected.get_data()
    corrCoords = corrected.coordmap
    stationary = load_image(stationaryFn)
    statData = stationary.get_data()
    statCoord = stationary.coordmap

    print(roiData.shape)
    if len(roiData.shape) == 4:
        roiData = np.average(roiData, axis=-1)

    maxCorr = 0.0
    maxCorrVol = 0
    correlations = []
    vols = []

    # Threshold the rois
    melodicData = np.abs(melodicData)
    roiData = np.abs(roiData)

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
    sortCorrVols = sorted(zip(correlations, vols), reverse=True)

    # TPR/FPR
    val = 0.1*np.amax(melodicData[:, :, :, maxCorrVol])
    threshComp = melodicData[:, :, :, maxCorrVol] > (val)

    tpr, fpr, tnr, fnr = calculateRates(roiData, threshComp) 

    # print results summary
    print("MELODIC extracted", melodicData.shape[-1], "components.")
    print("      Max correlation to DMN ROI:", maxCorr)
    print("  Component with max correlation:", maxCorrVol)
    print("                             TPR:", tpr)
    print("                             FPR:", fpr)
    print("                             TNR:", tnr)
    print("                             FNR:", fnr)

    # Save the results 
    with open(outFn, 'w') as f:
        f.write("correlation, component\n")
        
        for i in range(len(sortCorrVols)):
            f.write(str(sortCorrVols[i][0])+", "+str(sortCorrVols[i][1])+"\n")


    # Save best component info to spectr-level file
    if not os.path.exists(overviewFn):
        with open(overviewFn, 'w') as f:
            f.write("subject, registration, correlation, component, tpr, fpr, tnr, fnr\n")

    with open(overviewFn, 'a') as f:
        f.write(subjDir+", "+regtype+", "+str(maxCorr)+", "+str(maxCorrVol)+str(tpr)+", "+str(fpr)+", "+str(tnr)+", "+str(fnr)+"\n")


    # Print correlation between correctedData and BOLD data
#    print("Correlation between corrected "+regtype+" and BOLD:", np.correlate(corrData.flatten(), statData.flatten()))
#    print("Correlation between corrected "+regtype+" and roi: ", np.correlate(corrData.flatten(), roiData.flatten()))

if __name__ == "__main__":
    main()
