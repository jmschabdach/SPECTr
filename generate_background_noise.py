import numpy as np
from nipy.core.api import Image
from nipy import load_image, save_image
import argparse
from boldli import ImageManipulatingLibrary as mil

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
    
    return kImgShifted


##
# Generate a single 3D Gaussian distribution at a 
# specific location in the image
#
# @param img The image as a numpy array
# @param intensity Float value to scale the intensity of the distribution
#
# @returns newImg The distribution located at (x, y, z) in a blank image
def generateComplexGaussianNoise(imgshape, magIntensity=2.0, phaseIntensity=0.1):
    
    # Center of the image
    x = imgshape[0]
    y = imgshape[1]
    z = imgshape[2]
    
    # Generate Gaussian noise
    noise = [[[[magIntensity*np.random.standard_normal(), phaseIntensity*np.random.standard_normal()] for i in range(z)] for j in range(y)] for k in range(x)]
    noise = np.asarray(noise)
    print(noise[0, 0, 0])
    print(noise.shape)
    noise = 100*np.squeeze(noise.view(np.complex128))
    print(noise[0, 0, 0])
    
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
    # [X] Check this script to make sure it runs correctly
    # [X] Add argparse
    # [X] Generalize this script to generate noise for single volumes or large seqeuences

    # Add arguments to argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Image to add noise to')
    parser.add_argument('-o', '--output', type=str, help='Location to save noisy image')
    parser.add_argument('-s', '--scaling', type=float, help='Scaling factor for noise')

    args = parser.parse_args()

    # maskedVolFn = "masked_base_volume.nii.gz"
    # outFn = "noisy_volume.nii.gz"

    if args.scaling is None:
        scaling = 2.0
    else:
        scaling = args.scaling

    img = load_image(args.input)

    # Check image shape
    if len(img.get_data().shape) == 3:
        # Normalize signal range
        imgData = img.get_data()
        imgData *= (1000.0/np.max(imgData))

        # Perform the FFT
        kspace = volumeFFT(imgData)

        # Generate complex Gaussian noise
        noise = generateComplexGaussianNoise(kspace.shape, magIntensity=scaling)

        # Add complex Gaussian noise to the k-space image
        noisyKspace = addImages(kspace, noise)

        # Convert back to physical space
        noisyImg = volumeIFFTAndClean(noisyKspace)

        # Save noisy image
        save_image(Image(noisyImg, img.coordmap), args.output)

    elif len(img.get_data().shape) == 4:
        print(img.get_data().shape)

        noisyVols = []
        signalNormFactor = np.max(img.get_data())

        # Iterate through the volumes in the sequence
        for i in range(img.get_data().shape[-1]):
            # Isolate the volume
            vol = mil.isolateVolume(img, i)
            vol *= (1000.0/signalNormFactor)

            # Perform the FFT
            kspace = volumeFFT(vol)

            # Generate complex Gaussian noise
            noise = generateComplexGaussianNoise(kspace.shape, magIntensity=scaling)

            # Add complex Gaussian noise to the k-space image
            noisyKspace = addImages(kspace, noise)

            # Convert back to physical space
            newVol = volumeIFFTAndClean(noisyKspace)
            print(vol[22, 22, 22])
            print(newVol[22, 22, 22])
            noisyVols.append(newVol)

            print("Added noise to volume", i)

        noisySeq = mil.convertArrayToImage(noisyVols, img.coordmap)
        print(noisySeq.get_data().shape)
        # Save noisy image
        mil.saveBOLD(noisySeq, args.output)


if __name__ == "__main__":
    main()
