# class for star set
import numpy as np
from scipy.linalg import block_diag
import linalg

# should support comparing polytopes
class Polyhadron(object):
    pass

class Box(object):
    def __init__(self, lbs, ubs):
        lbs = np.array(lbs)
        ubs = np.array(ubs)
        assert (lbs.shape[0] == ubs.shape[0])
        self.dim = lbs.shape[0]
        v2 = np.vstack([lbs, ubs])
        self.lbs = np.amin(v2, axis = 0)
        self.ubs = np.amax(v2, axis = 0)
    
    def getStar(self):
        c = (self.lbs + self.ubs)/2.0
        vec = (self.ubs - self.lbs)/2.0
        
        C = np.hstack([np.eye(self.dim), -np.eye(self.dim)])
        D = np.hstack([np.ones(self.dim),np.ones(self.dim)])
        vs = []
        for idx in range(self.dim):
            tempv = np.zeros(self.dim)
            tempv[idx] = vec[idx]
            vs.append(tempv)
        
        vs = np.array(vs)
        return Star(c, vs, C, D)

    def __str__(self):
        ret_str = []
        for idx in range(self.dim):
            ret_str.append( str(self.lbs[idx]) + '-->' + str(self.ubs[idx]) )
        return 'Box : [' + ','.join(ret_str) + ']'




class Star (object):
    # preds * C <= D !!!
    # vs : [v0; v1; v2; ]  
    def __init__(self, center, vs, C, D):
        self.dim = center.shape[0]
        self.center = center
        self.vs = vs
        self.C = C
        self.D = D
        self.num_pred_var = C.shape[0]
        assert (self.dim == vs.shape[1])
        assert (self.num_pred_var == vs.shape[0])
        assert (C.shape[1] == D.shape[0])
    def copy(self):
        return Star(center = self.center, vs = self.vs, C = self.C, D=self.D)
    
    def ExtendDim(self, ilb, iub):
        add_dim = ilb.shape[0]
        assert (add_dim == iub.shape[0])
        #self.center = np.hstack([self.center, np.zeros(add_dim)])
        self.vs = np.hstack([self.vs, np.zeros((self.vs.shape[0], add_dim))])
        b = Box(ilb, iub)
        st = b.getStar()
        st.vs = np.hstack([np.zeros((st.vs.shape[0], self.dim)), st.vs])
        #st.center = np.hstack([np.zeros( self.dim), st.center])
        
        self.vs = np.vstack([self.vs, st.vs])
        self.center = np.hstack([self.center , st.center])
        self.C = block_diag(self.C, st.C)
        self.D = np.hstack([self.D, st.D])

        self.dim += add_dim
        self.num_pred_var += st.num_pred_var

        assert (self.dim == self.vs.shape[1])
        assert (self.num_pred_var == self.vs.shape[0])
        assert (self.C.shape[1] == self.D.shape[0])

    # x * W + b --> y
    def AffineTransform(self, W,b):
        assert (self.dim == W.shape[0])
        assert (W.shape[1] == b.shape[0])
        self.vs = np.matmul(self.vs, W)
        self.center = np.matmul(self.center, W) + b
        self.dim = W.shape[1]
    
    def isEmpty(self):
        return (not linalg.check_sat(self.C, self.D))

    # x * H <= g
    def ApplyHalfSpaceIntersection(self, H, g):
        ndim, n_ineq = H.shape
        assert ( n_ineq == g.shape[0])
        assert ( ndim == self.dim )
        newC = np.matmul( self.vs , H)
        newD = g - np.matmul( self.center, H )
        assert (newC.shape[0] == self.num_pred_var)
        assert (newC.shape[1] == newD.shape[0])

        self.C = np.hstack([self.C, newC])
        self.D = np.hstack([self.D, newD])
    
    def getBox(self):
        if self.num_pred_var == 0:
            return Box(lbs = self.center, ubs = self.center)
        
        if self.isEmpty():
            return None
        
        lbs, ubs = linalg.MinMaxOfStar(center = self.center, vs = self.vs, C=self.C, D=self.D)
        return Box(lbs, ubs)

    def __str__(self):
        retstr = 'STAR: center:' + str(self.center) + '\n'
        for vidx in range(self.num_pred_var):
            retstr += '  ' + str(self.vs[vidx]) + '\n'
        retstr += 'C= \n'+ str(self.C) + '\n'
        retstr += 'D= \n'+ str(self.D) + '\n'
        return (retstr)
        


if __name__ == "__main__":
    b0 = Box([1.0, -1.0], [2.0, 4.0])
    print (b0)
    s0 = b0.getStar()
    print (s0)
    print (s0.getBox())

    s0.ApplyHalfSpaceIntersection(np.array([[1.0],[1.0]]), np.array([2.0]))
    print (s0.getBox())

    s0.ExtendDim(np.array([-2]),np.array([1]))
    print (s0.getBox())
