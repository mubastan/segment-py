# 'Efficient Graph-Based Image Segmentation' (Felzenswalb IJCV 2005) in Python
# Original C++ code available at http://cs.brown.edu/~pff/segment/
# author: Muhammet Bastan, mubastan@gmail.com
# date: February 2012

from numpy import *
import operator
from DSF import *
from Edge import *

class EGBS:
    
    def __init__(self, width, height, threshold=300.0, minSize=100):
        self.W = width      # width of the image
        self.H = height     # height of the image
        self.setParameters(threshold, minSize)
        self.init(width, height)

    def setParameters(self, threshold=300, minSize=100):
        self.TH = float(threshold)
        self.MSZ = minSize
    
    def init(self, width, height):
        size = width*height
        nedges = 2*size - width - height
        print ('nedges: ', nedges)
        self.edges = array([Edge() for i in range(nedges)])
        self.dsf = DSF(size)
        self.thresholds = self.TH*ones(size)
    
    # number of sets/components in the segmentation
    def numSets(self):
        return self.dsf.numSets
        
    def segmentImage(self, image):
        self.numEdges = self.buildGraph(image)        
        print('number of edges: ', self.numEdges)
        print('number of sets initial: ', self.dsf.numSets)
        self.segmentGraph(self.numEdges)
        print('number of sets final: ', self.numSets())
        
    def segmentEdgeImage(self, edgeImage):        
        self.numEdges = self.buildEdgeGraph(edgeImage)
        print('number of edges: ', self.numEdges)
        print('number of sets initial: ', self.dsf.numSets)
        self.segmentGraph(self.numEdges)
        print('number of sets final: ', self.dsf.numSets)
        
    def buildGraph(self, image):
        w = image.shape[1]
        h = image.shape[0]
        numEdges = 0
        yw, ywx = 0, 0
        for y in range(h):
            yw = y*w
            for x in range(w):
                ywx = yw + x
                if x < w - 1:
                    dist = sqrt(sum((image[y,x,:] - image[y,x+1,:])**2))
                    self.edges[numEdges].set(ywx, ywx+1, dist)
                    numEdges += 1
                if y < h - 1:
                    dist = sqrt(sum((image[y,x,:] - image[y+1,x,:])**2))
                    self.edges[numEdges].set(ywx, ywx + w, dist)
                    numEdges += 1
        return numEdges
    
    # cmag: magnitude of color gradient, from color canny
    def buildEdgeGraph(self, cmag):
        w = cmag.shape[1]
        h = cmag.shape[0]
        numEdges = 0
        yw, ywx = 0, 0
        for y in range(h):
            yw = y*w
            for x in range(w):
                ywx = yw + x
                if x < w - 1:                    
                    self.edges[numEdges].set(ywx, ywx+1, cmag[y,x])
                    numEdges += 1
                if y < h - 1:                    
                    self.edges[numEdges].set(ywx, ywx + w, cmag[y,x])
                    numEdges += 1
        return numEdges
    
    def segmentGraph(self, numEdges):                
        self.edges.sort()
        for i in range(numEdges):
            #self.edges[i].printEdge()
            ed = self.edges[i]
            a = self.dsf.find(ed.a)
            b = self.dsf.find(ed.b)                        
            if a != b:
                w = ed.w
                if (w <= self.thresholds[a]) and (w <= self.thresholds[b]):
                    #tha = self.thresholds[a]
                    #thb = self.thresholds[b]
                    self.dsf.union(a, b)
                    a = self.dsf.find(a)
                    asize = self.dsf.nodes[a].size
                    self.thresholds[a] = w + float(self.TH)/(asize)
                    #self.thresholds[a] = w + float(self.TH+asize)/(asize*asize)
                    #self.thresholds[a] = w
                    
    
    # merge small components (post-processing)
    def mergeSmall(self, th = -1, numSegments=-1):
        for i in range(self.numEdges):            
            ed = self.edges[i]
            
            if th > 0 and ed.w > th: continue
            
            a = self.dsf.find(ed.a)
            b = self.dsf.find(ed.b)            
            if (a != b) and ( self.dsf.nodes[a].size < self.MSZ) or (self.dsf.nodes[b].size < self.MSZ):
                    self.dsf.union(a, b)
            if numSegments > 0 and self.dsf.numSets <= numSegments: break
    
    def getLabels(self):
        labels = zeros(self.H*self.W)        
        cids = []
        for pix in range(self.W*self.H):            
                cid = self.dsf.find(pix)
                if cid not in cids:
                    cids.append(cid)
                
                labels[pix] = cids.index(cid)
        labels.shape = (self.H, self.W)
        return labels
    def getSegmentEdges(self):
        labels = self.getLabels()        
        edges = zeros((self.H, self.W), dtype=bool)
        for y in range(self.H-1):
            for x in range(self.W-1):
                if labels[y,x] != labels[y, x+1] or labels[y,x] != labels[y+1, x]:
                    edges[y,x] = 255
        
        return labels, edges
    
import scipy
import sys
from pylab import *

if __name__ == "__main__":
    image = scipy.misc.imread(sys.argv[1])
    print('image.shape: ', image.shape)
    
    #pl.gray()
    imshow(image); draw()
    
    egbs = EGBS(image.shape[1], image.shape[0], threshold=300.0, minSize=100)
    egbs.segmentImage(image)
    print ('Merge small components')
    egbs.mergeSmall()
    print('number of sets final: ', egbs.numSets())
    
    labels = egbs.getLabels()
    matshow(labels)
    
    show()
