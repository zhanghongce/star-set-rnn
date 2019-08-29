import layer
import dataload
import timeoutalarm

np = layer.np


modelpath = "data/results/N7_L1_r11/"

testranges = [\
(0.000087 ,0.000115),
(0.027858 ,0.036758), #1
(0.111430 ,0.147033), #2
(0.891444 ,1.176267), #3
(0.000071 ,0.000142), 
(0.022627 ,0.045255), #5
(0.090510 ,0.181019), #6
(0.724077 ,1.448155), #7
(0.000062 ,0.000163),
(0.019698 ,0.051984),
(0.078793 ,0.207937), #
(0.630346 ,1.663493), #
(-0.000115,-0.000087),
(-0.036758,-0.027858),
(-0.147033,-0.111430),
(-1.176267,-0.891444), #
(-0.000142,-0.000071),
(-0.045255,-0.022627),
(-0.181019,-0.090510),
(-1.448155,-0.724077),
(-0.000163,-0.000062),
(-0.051984,-0.019698),
(-0.207937,-0.078793),
(-1.663493,-0.630346),
(0.362039 , 0.724077),
(0.315173 ,	0.831746),
(-0.724077,	-0.362039),
(-0.831746,	-0.315173),
(0.500000,	2.000000)
]

class TimeoutException(Exception):
    pass

def check_time(fn):
    with open(fn) as fin:
        if 'stopset' in fin.read():
            raise TimeoutException

def test_range(ilb, iub, init_state, W_rec, W_in, b, Nstimulus, Nsetttle , W_out, b_out, lockfile):
    
    if isinstance(ilb,float):
        ilb = np.array([ilb])
    elif isinstance(ilb, list):
        ilb = np.array(ilb)

    if isinstance(iub,float):
        iub = np.array([iub])
    elif isinstance(iub, list):
        iub = np.array(iub)
    
    if isinstance(init_state, list):
        init_state = np.array(init_state)

    slb = np.hstack([init_state, ilb])
    sub = np.hstack([init_state, iub])

    init_star = layer.star.Box(lbs=slb,ubs=sub).getStar()
    W_in_stimulus = W_in[0]
    W_layer_stimulus = np.vstack([W_rec, W_in_stimulus])
    l_stimulus = layer.Layer(W = W_layer_stimulus, b=b)

    prev_layer_polys = [init_star]

    for idx in range(Nstimulus):
        new_polys = []
        for st in prev_layer_polys:
            sts  = l_stimulus.reach(st)
            new_polys = new_polys + sts
        
        print ('stimulus layer = %d , # polys = %d' % (idx, len(new_polys)))
        if idx != Nsetttle -1 :
            for st in new_polys:
                st.ExtendDim(ilb, iub)
        
        prev_layer_polys = new_polys

        if len(new_polys)>4000:
            check_time(lockfile)
    
    # ------------------- SETTLE ----------------------------------
    W_in_settle = W_in[1] # * 1.0
    #W_layer_stimulus = np.vstack([W_rec, W_in_stimulus])
    l_settle = layer.Layer(W = W_rec, b= b + W_in_settle * 1.0)

    for idx in range(Nsetttle):
        new_polys = []
        for st in prev_layer_polys:
            sts  = l_settle.reach(st)
            new_polys = new_polys + sts
        
        print ('settle layer = %d , # polys = %d' % (idx, len(new_polys)))
        
        prev_layer_polys = new_polys

        if len(new_polys)>4000:
            check_time(lockfile)
    
    # ------------------- FINAL OUTPUT --------------------------
    N_pos = 0; N_neg = 0; N_unknown = 0
    for p in prev_layer_polys:
        p.AffineTransform(W_out, b_out)
        b = p.getBox()
        print (b)
        assert (b.lbs.shape[0] == 1 and b.ubs.shape[0] == 1)
        if (b.lbs >= 0).all() and (b.ubs >= 0).all():
            N_pos += 1
        elif (b.lbs <= 0).all() and (b.ubs <= 0).all():
            N_neg += 1
        else:
            N_unknown += 1
    return N_pos, N_neg, N_unknown
        


def test_all(logfile, lockfile, timeoutTime):
    weightsObj = dataload.LOADER(modelpath, 10)

    # clear the lock
    with open(lockfile,'w') as fout:
        fout.write('continue')

    with open(logfile,'w') as fout:
        for ilb, iub in testranges:
            print ('testing ', ilb, '-->', iub)
            print ('testing ', ilb, '-->', iub, file=fout, flush=True)
            start_time = time.time()
            try:
                with timeoutalarm.Timeout(timeoutTime,lockfile):
                    npos , nneg , nunknown = test_range(ilb, iub, weightsObj.init_state, weightsObj.W_rec, weightsObj.W_in, weightsObj.b_rec, 50, 50, weightsObj.W_out, weightsObj.b_out, \
                        lockfile)
                    print ('npos / nneg / nunknown = ', npos, nneg, nunknown)
                    print ('npos / nneg / nunknown = ', npos, nneg, nunknown, file=fout, flush=True)
            except TimeoutException:
                print ('TIMEOUT')
                print ('TIMEOUT', file=fout, flush=True)
            except KeyboardInterrupt:
                print ('SKIPPED')
                print ('SKIPPED', file=fout, flush=True)
            except Exception as e:
                print ('ERROR:')
                print (e)
                print ('ERROR', file=fout, flush=True)
                print (e, file=fout, flush=True)
            end_time = time.time()

            print ('Time : ', end_time-start_time)
            print ('Time : ', end_time-start_time, file=fout, flush=True)
            




if __name__ == "__main__":
    test_all('t1.log','t1.lock',4)
        

