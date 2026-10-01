function J=fixture_jacobian(t,y)
global FIXTURE_JAC_CALLS; FIXTURE_JAC_CALLS+=1;
J=sparse([-1,0;1,1]); assert(issparse(J));
end
