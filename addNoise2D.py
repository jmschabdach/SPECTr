import numpy as np
import matplotlib.pyplot as plt
import cv2                         # Installed in opencv

## 
# Load an image into a 2D numpy array where each element 
# is a value to display in grayscale
#
# @param fn The path to the file to load
#
# @returns img The loaded image
def loadImageGrayscale(fn):
    img = cv2.imread(fn, 0)
    return img

##
# Generate a single 2D Gaussian distribution at a 
# specific location in the image
#
# @param img The image as a numpy array
# @param x The x coordinate for the center of the distribution
# @param y The y coordinate for the center of the distribution
# @param diameter Int value specifying the diameter of the distribution in pixels
# @param intensity Float value to scale the intensity of the distribution
#
# @returns newImg The distribution located at (x, y) in a blank image
def generateBlur(img, x, y, diameter=50, intensity=1.0):

    # Generate the 2D Gaussian distribution 
    gridX, gridY = np.meshgrid(np.linspace(-1,1,diameter), 
                               np.linspace(-1,1,diameter))
    grid = np.sqrt(gridX*gridX+gridY*gridY)
    sigma = .5
    blur = intensity * np.exp(-((grid)**2/(2.0*sigma**2)))

    # Set up int values for zero padding
    lpad = int(np.round(x - (diameter/2.0)))
    rpad = int(np.round(img.shape[0] - lpad - (diameter)))
    upad = int(np.round(y - (diameter/2.0)))

    # Create a blank, image sized canvas
    newImg = np.zeros(img.shape)

    # Pad the distribution
    for row in range(len(blur)):
        newImg[row+upad] = np.pad(blur[row], (lpad, rpad), 
                                  'constant', constant_values=(0.0, 0.0))
    return newImg

##
# Additively combine 2 images
#
# @param img1 The first image
# @param img2 The second image
#
# @returns newImg The combination of img1 and img2
def addImages(img1, img2):
    newImg = np.add(img1, img2)
    return newImg

##
# Save the image to the specified location
#
# @param img The image to save (2D numpy array)
# @param fn Str specifying the location where the image should be saved to
def saveImage(img, fn):
    cv2.imwrite(fn, img)

def main():
    # Specify the name of the file to load
    inFn = "Lenna.png"
    outFn = "Lenna_spots.png"

    # Load the file
    lenna = loadImageGrayscale(inFn)

    # Generate some 2D Gaussian distributions
    spot1 = generateBlur(lenna, 150, 100, intensity=75)
    spot2 = generateBlur(lenna, 298, 401, intensity=80)
    spot3 = generateBlur(lenna, 417, 216, diameter=100, intensity=70)

    # Add the spots to the loaded image
    lennaSpots = addImages(lenna, spot1)
    lennaSpots = addImages(lennaSpots, spot2)
    lennaSpots = addImages(lennaSpots, spot3)

    # Save the image with spots in it
    saveImage(lennaSpots, outFn)

if __name__ == "__main__":
    main()
