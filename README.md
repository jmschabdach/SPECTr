## Simulated Phantom Emulating Cranial Transformations

### Pipeline: Using brain atlases

Step 1: Download the [ICBM Average Brain](https://www.mcgill.ca/bic/software/tools-data-analysis/anatomical-mri/atlases/icbm152lin "Average Brain") and the [funcional RIOs](https://findlab.stanford.edu/functional_ROIs.html "Functional ROIs") developed by Shirer et al. Unpack the downloads and put the following files in the same directory:

* mni_icbm152_lin_nifti/icbm_avg_152_t1_tal_lin.nii
* mni_icbm152_lin_nifti/icbm_avg_152_t1_tal_lin_mask.nii
* functional_rois/dorsal_DMN/dDMN.nii.gz
* functional_rois/ventral_DMN/vDMN.nii.gz

Let's call the new files

* dir/T1.nii
* dir/mask.nii
* dir/dDMN.nii.gz
* dir/vDMN.nii.gz 

respectively.

Step 2: Combine the dorsal and ventral default mode network ROIs into the same file. You will also need to specify a file with the desired coordinate system, as the ROI files are saved in a different coordinate system than the structural images we are using and need to be resampled accordingly.

The script `combine_rois.py` was created to combine 2 binary ROIs stored in .nii.gz files with the same dimensions and coordinates. Example: `python combine_rois.py -1 fMRI_Atlases/functional_rois/dorsal_DMN/dDMN.nii.gz -2 fMRI_Atlases/functional_rois/ventral_DMN/vDMN.nii.gz -c dir/T1.nii -o dmn_roi.nii.gz`

Step 3: Use the `apply_mask.py` script to apply the mask from the Average Brain data to the T1-weighted Average Brain to isolate the brain. Repeat for the ROI image.

The specific command is `python apply_mask.py -s /dir/T1.nii -m /dir/mask.nii -o /dir/masked_base_volume.nii.gz`. It also produces an image `./generated_brain_mask.nii.gz`, which is the mask for a single brain volume as calculated using Otsu thresholding.

Step 4: Use the `BaselineImageGenerator.py` script to replicate the `masked_base_volume.nii.gz` 149 times to create a sequence 150 volumes long.

The specific command is `python BaseImageGenerator.py -i /dir/masked_base_volume.nii.gz -o /dir/base_image_sequence.nii.gz`, and it creates the file `/dir/base_image_sequence.nii.gz` which is 150 copies of the volume in `/dir/masked_base_volume.nii.gz`

Step 5: Add Guassin noise to every image volume in k-space to imitate scanner noise.

`python generate_background_noise.py -i /dir/base_image_sequence.nii.gz -o /dir/image_sequence_noisy.nii.gz` 

Creates the image `/dir/image_sequence_noisy.nii.gz` in the directory of images. This sequence contains noise generated from a complex Gaussian distribution.

Step 6: Use the DMN ROIs to generate pseudo BOLD signal for the whole sequence. 

The specific command is `python generate_BOLD_signal.py -i /dir/image_sequence_noisy.nii.gz -r /dir/masked_dmn_roi.nii.gz -o /dir/image_sequence_bold.nii.gz`

Step 7: Add motion to the brain. The motion rotates the head around the center of the brain. The rotations are saved in a .csv file.

`python add_motion.py -i /dir/image_sequence_bold.nii.gz -o pseudo_BOLD.nii.gz`
