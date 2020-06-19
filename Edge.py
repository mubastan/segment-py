class Edge:
    def __init__(self, a=0, b=1, w=0):
        self.set(a, b, w)
        
    def set(self, a, b, w):
        self.a = a
        self.b = b
        self.w = w
    
#    def __cmp__(self,other):
#        return cmp(self.w, other.w)
    
    def __lt__(self, other):
         return self.w < other.w
        
    def printEdge(self):
        print(self.a, self.b, self.w)
