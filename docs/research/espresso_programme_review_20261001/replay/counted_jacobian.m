function J=counted_jacobian(t,u)
global CAMMON;
a=tic(); J=rhs_jacobian(t,u,CAMMON.params,CAMMON.x,CAMMON.A); cost=toc(a);
CAMMON.jac_calls+=1; CAMMON.jac_seconds+=cost;
CAMMON.jac_max_trial_time=max(CAMMON.jac_max_trial_time,t);
CAMMON.jac_all_sparse=CAMMON.jac_all_sparse && issparse(J);
end
