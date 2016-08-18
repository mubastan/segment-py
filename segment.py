# Color Image Segmentation in Python (driver)
# 2 algorithms:
#       1. Efficient Graph Based Image Segmentation (EGBS), by Felzenswalb et. al, IJCV 2004
#       2. Statistical Region Merging (SRM), by Nock and Nielsen, PAMI 2004
#
# author: Muhammet Bastan, mubastan@gmail.com
# date: February 2012

import sys, os
from pylab import *
from numpy import *
import scipy
import operator
import scipy.ndimage
from EGBS import *
from SRM import *

## Segment color image, using the 'Efficient Graph Based Image Segmentation' (EGBS) and show the results
def segmentColorImageEGBS(file):
    image = scipy.ndimage.imread(file)
    h, w, d = image.shape
    print 'image.shape: ', image.shape
    imshow(image); title('Input image'); draw()
    
    TH = 500    # threshold
    print 'TH:', TH    
    egbs = EGBS(w, h, threshold=TH, minSize=500)
    egbs.segmentImage(image)
    print 'Merge small components'
    egbs.mergeSmall()
    print 'number of segments: ', egbs.numSets()
    
    #labels = egbs.getLabels()
    labels, edges = egbs.getSegmentEdges()
    gray()
    matshow(labels); title('Segmentation'); draw()
    matshow(edges); title('edges'); draw()
    
    image2 = image.copy()
    image2[edges==0] = (0,0,0)
    figure(); imshow(image2); draw()

## Segment color image, using the 'Statistical Region Merging' (SRM) and show the results
def segmentColorImageSRM(file):
    
    fname, fext = os.path.splitext(file)
    
    image = scipy.misc.imread(file, False)    
    
    image = scipy.ndimage.filters.median_filter(image, 3)
    image = scipy.ndimage.filters.gaussian_filter(image, 0.5)

    imshow(image); title('Input image'); draw()   
    
    h, w, d = image.shape
    srm = SRM(w, h, d)
    srm.segmentImage(image, 45)
    # srm.segmentImage2(image, Gm, 128) # using gradient magnitudes Gm (e.g., from color Canny edge detection)
    print 'Merge small components'
    srm.mergeSmall(minsize=10)
    print 'number of segments: ', srm.numSets()
    
    labels, edges = srm.getSegmentEdges()
    
    matshow(labels); title('Segmentation'); gray(); draw()
    matshow(edges); title('edges'); gray(); draw()


# input: edge gradient magnitudes
def segmentEdgeImage(file):
    #Load gradient magnitude from numpy file *.npy
    Gm = numpy.load(file)
    h, w = Gm.shape
    matshow(Gm); gray(); title('Gradient magnitude'); draw()
    
    Gm = scipy.ndimage.filters.gaussian_filter(Gm, 0.5) 
    
    MX = Gm.max()    
    Gm *= 255.0/MX
    
    MN = mean(Gm)
    MD = median(Gm)
    print 'mean, median, max: ', MN, MD, 255
    
    Gm[Gm < MD] = 0.0        
    TH = 700
    print 'TH:', TH    
    egbs = EGBS(w, h, threshold=TH, minSize=300)
    egbs.segmentEdgeImage(Gm)
    print 'Merge small components'
    egbs.mergeSmall(th=100, numSegments=20)
    print 'number of segments: ', egbs.numSets()
    
    labels, edges = egbs.getSegmentEdges()
    matshow(labels); title('Segmentation labels'); gray(); draw()
    matshow(edges); title('Segmentation edges'); gray(); draw()

def showEdgeColors(imgfile, edgefile):
    image = scipy.misc.imread(imgfile)
    edge = scipy.misc.imread(edgefile)
    
    imshow(image); draw()
    figure(); imshow(edge); gray(); draw()
    
    image2 = image.copy()
    #edge = scipy.ndimage.morphology.binary_dilation(edge, iterations=2)
    edge = scipy.ndimage.morphology.binary_closing(edge, iterations=1)
    image2[edge==0] = (255,255,0)
    
    grayImg = scipy.misc.imread(imgfile, True)
    edge2 = scipy.ndimage.morphology.morphological_gradient(grayImg, size=(3,3))    
     
    figure(); imshow(edge); gray(); draw()
    figure(); imshow(edge2); gray(); title('morphology edge'); draw()
    figure(); imshow(image2); draw()   
    

if __name__ == "__main__":
    if len(sys.argv) < 2: print '\nUsage: python segment.py imageFile\n'; sys.exit()
    
    
    #segmentColorImageEGBS(sys.argv[1])
    segmentColorImageSRM(sys.argv[1])
    #segmentEdgeImage(sys.argv[1])
   
    show()