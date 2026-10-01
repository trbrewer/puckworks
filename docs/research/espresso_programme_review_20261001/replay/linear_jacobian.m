function A=linear_jacobian(p,x)
% Exact linear stencils of source RHS.m; no mass inversion.
N=p(1); dx=p(2); D=p(3); gamma=1/(1-p(12)); q=p(13);
n=N+2*N*N; A=sparse(n,n);
A(1,1:3)=[1.5*D/dx+q,-2*D/dx,.5*D/dx];
for j=2:N-1
 A(j,j-1:j+1)=gamma*[D/dx^2+q/(2*dx),-2*D/dx^2,D/dx^2-q/(2*dx)];
end
A(N,N-2:N)=[.5,-2,1.5];
for family=1:2
 Ds=p(3+family); B=sparse(N,N);
 for i=1:N-1
  edge=4*pi*((x(i)+x(i+1))/2)^2*Ds/dx;
  B(i,i)=B(i,i)-edge; B(i,i+1)=B(i,i+1)+edge;
  B(i+1,i)=B(i+1,i)+edge; B(i+1,i+1)=B(i+1,i+1)-edge;
 end
 ix=N+(family-1)*N*N+(1:N*N);
 A(ix,ix)=kron(speye(N),B);
end
end
