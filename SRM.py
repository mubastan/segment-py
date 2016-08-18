# 'Statistical Region Merging' (SRM), by Nock and Nielsen, PAMI 2004, in Python
# 
# author: Muhammet Bastan, mubastan@gmail.com
# date: February 2012

import numpy
from numpy import *
import operator
from DSF import *
from Edge import *

class SRM:
    
    def __init__(self, width, height, channels):
        self.W = width      # width of the image
        self.H = height     # height of the image
        self.D = channels
        self.init(width, height)
        #self.means = None
    
    def init(self, width, height):
        size = width*height
        nedges = 2*size - width - height
        print 'number edges allocated: ', nedges
        self.edges = array([Edge() for i in range(nedges)])
        self.dsf = DSF(size)
        
    
    # number of sets/components in the segmentation
    def numSets(self):
        if self.dsf: return self.dsf.numSets
        else: return -1
        
    def segmentImage(self, image, Q):
        self.initMeansColor(image)        
        self.numEdges = self.buildGraph(image)        
        print 'number of edges: ', self.numEdges
        print 'number of sets initial: ', self.dsf.numSets
        self.segmentGraph(self.numEdges, Q)
        print 'number of sets final: ', self.numSets()
    
    def segmentImage2(self, image, Gm, Q):
        self.initMeansColor(image)        
        self.numEdges = self.buildEdgeGraph(Gm)        
        print 'number of edges: ', self.numEdges
        print 'number of sets initial: ', self.dsf.numSets
        self.segmentGraph(self.numEdges, Q)
        print 'number of sets final: ', self.numSets()
    
    def initMeansColor(self, image):
        w = image.shape[1]
        h = image.shape[0]
        d = 1
        if len(image.shape) == 3: d = image.shape[2]
        self.D = d
        self.means = zeros((d, h*w))
        if d==1: self.means[0] = image.ravel()
        else:
            for i in range(d): self.means[i] = image[:,:,i].ravel()        
    
    def buildGraph(self, image):
        #return self.buildGraph1(image[:,:,2])
        if self.D == 1: return self.buildGraph1(image)
        
        w = image.shape[1]
        h = image.shape[0]
        numEdges = 0
        yw, ywx = 0, 0
        for y in range(h):
            yw = y*w
            for x in range(w):
                ywx = yw + x
                if x < w - 1:
                    dist = numpy.fabs((image[y,x,:] - image[y,x+1,:])).max()                    
                    self.edges[numEdges].set(ywx, ywx+1, dist)
                    numEdges += 1
                if y < h - 1:                    
                    dist = numpy.fabs((image[y,x,:] - image[y+1,x,:])).max()
                    self.edges[numEdges].set(ywx, ywx + w, dist)
                    numEdges += 1
        return numEdges
    
    # for single channel image
    def buildGraph1(self, image):
        w = image.shape[1]
        h = image.shape[0]
        numEdges = 0
        yw, ywx = 0, 0
        for y in range(h):
            yw = y*w
            for x in range(w):
                ywx = yw + x
                if x < w - 1:
                    dist = numpy.fabs((image[y,x] - image[y,x+1]))
                    self.edges[numEdges].set(ywx, ywx+1, dist)
                    numEdges += 1
                if y < h - 1:                    
                    dist = numpy.fabs((image[y,x] - image[y+1,x]))
                    self.edges[numEdges].set(ywx, ywx + w, dist)
                    numEdges += 1
        return numEdges
    
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
    
    def segmentGraph(self, numEdges, Q):                
        self.edges.sort()
        logdelta = 2.0*log(6.0*self.W*self.H);
        NUM_GRAY = 256
        threshfactor = (NUM_GRAY*NUM_GRAY)/(2.0*Q)
        for i in range(numEdges):            
            ed = self.edges[i]
            a = self.dsf.find(ed.a)
            b = self.dsf.find(ed.b)                        
            if a != b:
                size1 = float(self.dsf.setSize(a))
                size2 = float(self.dsf.setSize(b))
                threshold=numpy.sqrt(threshfactor*(((numpy.minimum(NUM_GRAY,size1)*log(1.0+size1)+logdelta)/size1)+((numpy.minimum(NUM_GRAY,size2)*log(1.0+size2)+logdelta)/size2)));
                md = sum(numpy.fabs(self.means[:,a] - self.means[:,b]) < threshold)
                if md == self.means.shape[0]:                    
                    self.dsf.union(a, b)
                    ab = self.dsf.find(a)
                    # update the mean
                    self.means[:, ab] = (size1*self.means[:,a] + size2*self.means[:,b])/(size1+size2)
    
    # merge small components (post-processing)
    def mergeSmall(self, minsize = 100, th = -1, numSegments=-1):
        for i in range(self.numEdges):            
            ed = self.edges[i]
            
            #if th > 0 and ed.w > th: continue
            
            a = self.dsf.find(ed.a)
            b = self.dsf.find(ed.b)            
            if (a != b) and ( self.dsf.nodes[a].size < minsize) or (self.dsf.nodes[b].size < minsize):
                    self.dsf.union(a, b)
            #if numSegments > 0 and self.dsf.numSets <= numSegments: break
    
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