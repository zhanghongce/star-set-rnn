import cplex

# check pred * C <= D has solution?
def check_sat(C,D):
    n_var = C.shape[0]
    n_ineq = C.shape[1]
    assert (n_ineq == D.shape[0])

    pred_vars = ['pred_%d' % idx for idx in range(n_var)]
    solver = cplex.Cplex()
    solver.variables.add(names = pred_vars, lb = [-cplex.infinity]*n_var, ub = [cplex.infinity]*n_var, \
        types = [solver.variables.type.continuous] * n_var)

    lhs = [ [ list(range(n_var)) ,coefs  ] for coefs in (C.T).tolist() ]
    solver.linear_constraints.add(lin_expr= lhs, rhs = D.tolist(), senses='L'*(D.shape[0]))
    #solver.linear_constraints.add(lin_expr= [[1.0,0.0],[0.0,1.0]], rhs =[1.0,2.0], senses='L'*(2))
    
    solver.set_log_stream(None)
    solver.set_warning_stream(None)
    solver.set_error_stream(None)
    solver.set_results_stream(None)
    solver.solve()
    try:
        _ = solver.solution.get_values(pred_vars)
    except:
        return False
    return True

# return two lists of names
def EncodeStar(center, vs, C, D, solver):
    assert (len(center.shape) == 1)
    n_dim = center.shape[0]
    n_pred = vs.shape[0]
    assert (vs.shape[1] == n_dim)
    assert (C.shape[0] == n_pred)
    assert (len(D.shape) == 1)
    n_constr = C.shape[1]
    assert (n_constr == D.shape[0])
    pnts = ['p_%d' % idx for idx in range(n_dim)]
    preds = ['pred_%d' % idx for idx in range(n_pred)]

    solver.variables.add(names = preds, lb = [-cplex.infinity]*n_pred, ub = [cplex.infinity]*n_pred, \
        types = [solver.variables.type.continuous] * n_pred)
    solver.variables.add(names = pnts, lb = [-cplex.infinity]*n_dim, ub = [cplex.infinity]*n_dim, \
        types = [solver.variables.type.continuous] * n_dim)
    
    coefs = []
    rhs = []
    for d in range(n_dim):
        index = [pnts[d]]
        vals = [1.0]
        #coef = [cplex.SparsePair(ind = pnts[d], val = 1.0)]
        right = float(center[d])
        for pidx in range(n_pred):
            index.append(preds[pidx])
            vals.append(-float(vs[pidx][d]))
        coefs.append(cplex.SparsePair(ind = index, val = vals))
        rhs.append(right)
    assert (len(coefs) == len(rhs))
    #print (coefs)
    #print (rhs)
    solver.linear_constraints.add(lin_expr=coefs, rhs=rhs, senses='E'*(len(rhs)))

    lhs = [ [ list(range(n_pred)) ,coefficient  ] for coefficient in (C.T).tolist() ]
    #print (lhs)
    #print (D.tolist())
    solver.linear_constraints.add(lin_expr= lhs, rhs = D.tolist(), senses='L'*(D.shape[0]))
    return pnts, preds
    
def MinMaxOfStar(center, vs, C, D):
    assert (len(center.shape) == 1)
    n_dim = center.shape[0]
    n_pred = vs.shape[0]
    assert (vs.shape[1] == n_dim)
    assert (C.shape[0] == n_pred)
    assert (len(D.shape) == 1)
    n_constr = C.shape[1]
    assert (n_constr == D.shape[0])

    ubs = []
    lbs = []
    for d in range(n_dim):
        solver = cplex.Cplex()
        xs, _ = EncodeStar(center, vs, C, D, solver)
        solver.objective.set_linear(xs[d],1.0)
        solver.objective.set_sense(solver.objective.sense.maximize)
        solver.set_log_stream(None)
        solver.set_warning_stream(None)
        solver.set_error_stream(None)
        solver.set_results_stream(None)
        solver.solve()
        ub = solver.solution.get_values(xs[d])
        ubs.append(ub)
        
        solver.objective.set_sense(solver.objective.sense.minimize)
        solver.solve()
        lb = solver.solution.get_values(xs[d])
        lbs.append(lb)
    """
        solver = cplex.Cplex()
        xs, _ = EncodeStar(center, vs, C, D, solver)
        solver.objective.set_linear(xs[d],1.0)
        solver.objective.set_sense(solver.objective.sense.minimize)
        solver.set_log_stream(None)
        solver.set_warning_stream(None)
        solver.set_error_stream(None)
        solver.set_results_stream(None)
        solver.solve()
        lb = solver.solution.get_values(xs[d])
        lbs.append(lb)
    """
    return lbs, ubs



    


if __name__ == "__main__":
    import numpy as np
    # do some test
    C = np.array([[1.0,0.0],[0.0,1.0], [-1.0,-1.0]]).T
    D = np.array([1.0,2.5,5])
    print (check_sat(C,D))