function J=rhs_jacobian(t,u,p,x,A)
% dRHS/du, NOT d(M^-1 RHS)/du and NOT the IDA residual Jacobian.
% G=K*(1-l)*s*(s-beta*l):
% dG/dl=-K*s*(s+beta-2*beta*l); dG/ds=K*(1-l)*(2*s-beta*l).
N=p(1); K=p(8); beta=p(11); gamma=1/(1-p(12));
l=u(1:N); J=A;
for family=1:2
 surf=N+(family-1)*N*N+(1:N)'*N;
 s=u(surf); dl=-K*s.*(s+beta-2*beta*l);
 ds=K*(1-l).*(2*s-beta*l); bet=p(5+family); Q=p(8+family);
 j=(2:N-1)'; allj=(1:N)';
 rows=[j;j;surf;surf]; cols=[j;surf(j);allj;surf];
 values=[gamma*bet*dl(j);gamma*bet*ds(j);-4*pi*beta*Q*dl;-4*pi*beta*Q*ds];
 J=J+sparse(rows,cols,values,size(A,1),size(A,2));
end
assert(issparse(J));
end
