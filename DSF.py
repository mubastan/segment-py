
from numpy import *

class Node:
    def __init__(self, parent, rank = 0):
        self.parent = parent
        self.rank = rank
        self.size = 1 
        

class DSF:
    def __init__(self, numElements):
        self.numElements = numElements
        self.numSets = numElements
        self.nodes = array([Node(i) for i in range(numElements)])
    
    def find(self, x):
        y = x
        while y != self.nodes[y].parent:
            y = self.nodes[y].parent
        self.nodes[y].parent = y
        return y
    
    def union(self, x, y):        
        xr = self.find(x)        # root, set of x
        yr = self.find(y)        # root, set of y
        if(x==y or xr==yr): return
        nx = self.nodes[xr]
        ny = self.nodes[yr]
        if nx.rank > ny.rank:
            ny.parent = xr
            nx.size += ny.size
        else:
            nx.parent = yr
            ny.size += nx.size
            if nx.rank == ny.rank:
                ny.rank += 1
        self.numSets -= 1
    
    def setSize(self, id):
        return self.nodes[id].size
    
    def reset(self):
        for i in range(self.numElements):
            self.nodes[i].rank = 0
            self.nodes[i].size = 1
            self.nodes[i].parent = i
        self.numSets = self.numElements
    
    def printSet(self):
        print '\nnum elements: ', self.numElements
        print 'num sets: ', self.numSets
        print 'Size: '
        for i in range(self.numElements):
            print self.nodes[i].size,
        print '\nParent: '
        for i in range(self.numElements):
            print self.nodes[i].parent,
        print '\nRank: '
        for i in range(self.numElements):
            print self.nodes[i].rank,
        
if __name__ == "__main__":
    dsf = DSF(10)
    print 'dsf.numElements: ', dsf.numElements
    print 'dsf.numSets: ', dsf.numSets
    print 'find 3: ', dsf.find(3)
    print 'find 4: ', dsf.find(4)
    dsf.union(3,4)
    print 'union 3,4'
    print 'find 3: ', dsf.find(3)
    print 'find 4: ', dsf.find(4)
    dsf.union(3,5)
    print 'union 3,5'
    print 'find 3: ', dsf.find(3)
    print 'find 5: ', dsf.find(5)
    print 'num sets:', dsf.numSets
    
    dsf.printSet()
    dsf.union(9,4)
    dsf.union(0,1)
    dsf.printSet()
    dsf.union(0,5)
    dsf.printSet()
    dsf.reset()
    dsf.printSet()