#!/usr/bin/bash

## Simulated Phantom Emulating Cranial Transformations

### Pipeline: Using brain atlases

# # Step 1: Download the [ICBM Average Brain](https://www.mcgill.ca/bic/software/tools-data-analysis/anatomical-mri/atlases/icbm152lin "Average Brain") and the [funcional RIOs](https://findlab.stanford.edu/functional_ROIs.html "Functional ROIs") developed by Shirer et al. Unpack the downloads and put the following files in the same directory:
# 
# * mni_icbm152_lin_nifti/icbm_avg_152_pd_tal_lin.nii
# * mni_icbm152_lin_nifti/icbm_avg_152_t1_tal_lin_mask.nii
# * functional_rois/dorsal_DMN/dDMN.nii.gz
# * functional_rois/ventral_DMN/vDMN.nii.gz
# 
# #Let's call the new files
# 
# * sandbox/PD_orig.nii
# * sandbox/mask_orig.nii
# * sandbox/dDMN_orig.nii.gz
# * sandbox/vDMN_orig.nii.gz 

# Resample all of these images so that the new spatial resolution is 4mm x 4mm x 4mm

python downsample_images.py -i sandbox/PD_orig.nii -o sandbox/PD.nii
python downsample_images.py -i sandbox/mask_orig.nii -o sandbox/mask.nii
python downsample_images.py -i sandbox/dDMN_orig.nii.gz -o sandbox/dDMN.nii.gz
python downsample_images.py -i sandbox/vDMN_orig.nii.gz -o sandbox/vDMN.nii.gz

# Step 2: Combine the dorsal and ventral default mode network ROIs into the same file. You will also need to specify a file with the desired coordinate system, as the ROI files are saved in a different coordinate system than the structural images we are using and need to be resampled accordingly.
 
echo "------------------------"
echo "Combining ROIS"
python combine_rois.py -1 sandbox/dDMN.nii.gz -2 sandbox/vDMN.nii.gz -c sandbox/PD.nii -o sandbox/dmn_roi.nii.gz
echo "Complete"

# Step 3: Use the `apply_mask.py` script to apply the mask from the Average Brain data to the T1-weighted Average Brain to isolate the brain. Repeat for the ROI image.

echo "------------------------"
echo "Applying mask to input images"
python apply_mask.py -s sandbox/PD.nii -m sandbox/mask.nii -o sandbox/masked_base_volume.nii.gz
python apply_mask.py -s sandbox/dmn_roi.nii.gz -m sandbox/mask.nii -o sandbox/masked_dmn_roi.nii.gz
echo "Complete"
 
# Step 4: Use the `BaselineImageGenerator.py` script to replicate the `masked_base_volume.nii.gz` 149 times to create a sequence 150 volumes long.
 
echo "------------------------"
echo "Generating the baseline image sequence"
python BaseImageGenerator.py -i sandbox/masked_base_volume.nii.gz -o sandbox/base_image_sequence.nii.gz
echo "Complete"
 
# Step 5: Use the DMN ROIs to generate pseudo BOLD signal for the whole sequence. 

echo "------------------------"
echo "Generating the BOLD signal"
python generate_BOLD_signal.py -s sandbox/base_image_sequence.nii.gz -r sandbox/masked_dmn_roi.nii.gz -o sandbox/image_sequence_bold.nii.gz
echo "Complete"

# Step 6: Add Guassian noise to every image volume in k-space to imitate scanner noise.

echo "------------------------"
echo "Adding scanner noise"
python generate_background_noise.py -i sandbox/image_sequence_bold.nii.gz -o sandbox/image_sequence_noisy.nii.gz -s 1
echo "Complete"

# Step 7: Add motion to the brain. The motion rotates the head around the center of the brain. The rotations are saved in a .csv file.

echo "------------------------"
echo "Adding motion to the brain"
python add_motion.py -i sandbox/image_sequence_noisy.nii.gz -o sandbox/pseudo_BOLD.nii.gz
echo "Complete"

