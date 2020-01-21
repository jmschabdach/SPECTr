from nipy import load_image
from skimage.measure import regionprops
import argparse
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help="Image that needs center of mass identified")
    args = parser.parse_args()

    # Load the image
    img = load_image(args.input)
    # Get the image data
    data = img.get_data()
    # Threshold the data
    labeled = (data > 0).astype(int)
    # Calculate the properties of the data
    properties = regionprops(labeled, data)
    # Print the centroid
    centroid = properties[0].centroid
    # Round to get the center of mass in voxels
    com = [int(round(i)) for i in centroid]

    # Create the name for the output file
    path = os.path.dirname(args.input)
    outFn = os.path.join(path, "center_of_mass.txt")

    with open(outFn, "w") as f:
        f.write(str(com))

    print("Center of mass located at:", com)

if __name__ == "__main__":
    main()

