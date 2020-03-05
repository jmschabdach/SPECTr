rm -rf ./testing_melodic/
melodic -i sandbox/pseudo_BOLD.nii.gz --report -o testing_melodic --Oall
fslcc --noabs -p 3 -t 0.005 sandbox/dmn_roi.nii.gz testing_melodic/melodic_IC.nii.gz

