import star

np = star.np

# for a layer
class Layer(object):
    # s * W + b
    def __init__(self, W, b , RELU_output = True):
        self.W = W
        self.b = b
        self.input_dim = W.shape[0]
        self.output_dim = W.shape[1]
        self.RELU_output = RELU_output
        assert (b.shape[0] == self.output_dim)

    def reach(self, s: star.Star): # s is one star
        #print (s)
        #print (s.getBox())
        #print (self.W)
        #print (self.b)
        #try:
        s.AffineTransform(self.W, self.b)
        #except Exception as e:
        #    print (s.dim)
        #    print (self.W)
        #    print (self.b)
        #    raise e
        #print (s)
        #apply halfspace intersection
        #print (s.getBox())
        stars = [s]
        if self.RELU_output:
            for d in range(self.output_dim):
                new_stars = []
                for s in stars:
                    P = s
                    N = s.copy()
                    
                    H1 = np.zeros((self.output_dim,1))
                    H1[d] = -1.0
                    G1 = np.array([0.0])

                    P.ApplyHalfSpaceIntersection(H1, G1)
                    if not P.isEmpty():
                        new_stars.append(P)
                    #else:
                    #    print ('Empty')

                    H1[d] = 1.0 # 1.0 * xn <= 0
                    N.ApplyHalfSpaceIntersection(H1, G1)
                    if not N.isEmpty():
                        W1 = np.eye(self.output_dim)
                        W1[d][d] = 0
                        N.AffineTransform(W1, np.zeros(self.output_dim))
                        new_stars.append(N)
                    #else:
                    #    print ('Empty')
                stars = new_stars
        return stars



if __name__ == "__main__":
    # let's have a simple test
    ilb = -1.0 ; iub = 1.0
    s = [0.1,1.2]
    nlayer = 10

    slb = s[:]+[ilb]
    sub = s[:]+[iub]
    init_star = star.Box(lbs=slb,ubs=sub).getStar()
    
    W_rec = np.array([[0.1,0.2],[0.3,-0.4]]).T
    W_in = np.array([0.2,-0.1])
    b = np.array([-0.2,0.5])

    W_layer = np.vstack([W_rec, W_in])
    l = Layer(W = W_layer, b=b)

    prev_layer_polys = [init_star]
    for idx in range(nlayer):
        new_polys = []
        for st in prev_layer_polys:
            sts  = l.reach(st)
            new_polys = new_polys + sts
        
        print ('layer = %d , # polys = %d' % (idx, len(new_polys)))
        for st in new_polys:
            st.ExtendDim(np.array([ilb]), np.array([iub]))
        
        prev_layer_polys = new_polys
        


