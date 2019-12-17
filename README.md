## Simulated Phantom Emulating Cranial Transformations

### Pipeline 1: Using an existing sequence

Let's call the existing sequence `BOLD.nii.gz`

Step 1: Use the `BaselineImageGenerator.py` to isolate a volume from the image sequence and replicate it to create a sequence 150 volumes long. Also generates a mask of the brain using Otsu thresholding.

The command

Step 2: Add speckle to imitate scanner noise

Step 3: Generate 3D Gaussian disributions as pseudo BOLD signal and add them to the baseline sequence.

Step 4: Limit the pseudo BOLD signal to only areas inside the brain mask. Use `apply_mask.py`

Step 5: Add motion to the brain. The motion rotates the head around the center of the brain. The rotations are saved in a .csv file.

### Pipeline 2: Using brain atlases

Step 1: Download the [ICBM Average Brain](https://www.mcgill.ca/bic/software/tools-data-analysis/anatomical-mri/atlases/icbm152lin "Average Brain") and the [funcional RIOs](https://findlab.stanford.edu/functional_ROIs.html "Functional ROIs") developed by Shirer et al. Unpack the downloads and put the following files in the same directory:

* mni_icbm152_lin_nifti/icbm_avg_152_t1_tal_lin.nii
* mni_icbm152_lin_nifti/icbm_avg_152_t1_tal_lin_mask.nii
* functional rois/dorsal_DMN/dDMN.nii.gz
* functional rois/ventral_DMN/vDMN.nii.gz

Let's call the new files

* dir/T1.nii
* dir/mask.nii
* dir/dDMN.nii.gz
* dir/vDMN.nii.gz 

respectively.

Step 2: Use the `apply_mask.py` script to apply the mask from the Average Brain data to the T1-weighted Average Brain to isolate the brain.

The specific command is `python apply_mask.py -s /dir/T1.nii -m /dir/mask.nii -o /dir/masked_base_volume.nii.gz`. It also produces an image `./generated_brain_mask.nii.gz`, which is the mask for a single brain volume as calculated using Otsu thresholding.

Step 3: Use the `BaselineImageGenerator.py` script to replicate the `masked_base_volume.nii.gz` 149 times to create a sequence 150 volumes long.

The specific command is `python BaseImageGenerator.py -i /dir/masked_base_volume.nii.gz -o /dir/base_image_sequence.nii.gz`, and it creates the file `/dir/base_image_sequence.nii.gz` which is 150 copies of the volume in `/dir/masked_base_volume.nii.gz`

Step 4: Add speckle to every image volume to imitate scanner noise.

Step 5: Combine the dorsal and ventral default mode network ROIs into the same file

Step 6: Use the DMN ROIs to generate pseudo BOLD signal for the whole sequence

Step 7: Add motion to the brain. The motion rotates the head around the center of the brain. The rotations are saved in a .csv file.

