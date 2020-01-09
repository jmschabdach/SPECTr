import numpy as np
from nipy.core.api import Image
from nipy import load_image, save_image

##
# Perform the fast Fourier transform on an image and return the magnitude and phase images
#
# @param img The image as a numpy array
#
# @returns kImgShifted The complex image in k-space
def volumeFFT(img):
    # Perform the FFT on the image
    kImg = np.fft.fftn(img)
    
    # Use FFT shift to center the spectrum
    kImgShifted = np.fft.fftshift(kImg)
    print(np.max(kImgShifted), np.min(kImgShifted))
    
    return kImgShifted


##
# Generate a single 3D Gaussian distribution at a 
# specific location in the image
#
# @param img The image as a numpy array
# @param intensity Float value to scale the intensity of the distribution
#
# @returns newImg The distribution located at (x, y, z) in a blank image
def generateComplexGaussianNoise(imgshape, intensity=1.0):
    
    # Center of the image
    x = imgshape[0]
    y = imgshape[1]
    z = imgshape[2]
    
    # Generate Gaussian noise
    noise = np.squeeze(np.random.standard_normal(size=(x, y, z, 2)).view(np.complex128))
    print(noise.shape)
    
    # Amplify the noise as needed
    noise *= intensity
    
    return noise


##
# Additively combine 2 images
#
# @param img1 The first image as a numpy array
# @param img2 The second image as a numpy array
#
# @returns newImg The combination of img1 and img2
def addImages(img1, img2):
    newImg = np.add(img1, img2)
    return newImg


##
# Convert magnitude and phase images back to a physical space image
#
# @param kImg The complex k-space image
#
# @return img The physical space image
def volumeIFFTAndClean(kImg):
    
    # Unshift the combined image
    kImg = np.fft.ifftshift(kImg)
    
    # Perform the IFFT
    img = np.fft.ifftn(kImg)
    
    img = np.real(img)
    img *= (1000.0/np.max(img))
    img = np.around(img, 8)
    img[img < 0.0] = 0
    img[img > 1000.0] = 1000.0
    
    return img


def main():
    # NEXT
    # [ ] Check this script to make sure it runs correctly
    # [ ] Add argparse
    # [ ] Generalize this script to generate noise for single volumes or large seqeuences
    # Images to check
    maskedVolFn = "masked_base_volume.nii.gz"

    img = load_image(maskedVolFn)

    imgData = img.get_data()
    print(np.max(imgData), np.min(imgData))
    imgData *= (1000.0/np.amax(imgData))
    print(np.max(imgData), np.min(imgData))

    # Perform the FFT
    kspace = volumeFFT(imgData)

    # Generate complex Gaussian noise
    noise = generateComplexGaussianNoise(kspace.shape)
    print(np.max(noise), np.min(noise))

    # Add complex Gaussian noise to the k-space image
    noisyKspace = addImages(kspace, noise)

    # Convert back to physical space
    noisyImg = volumeIFFT(noisyKspace)

    print(np.max(noisyImg), np.min(noisyImg))


if __name__ == "__main__":
    main()