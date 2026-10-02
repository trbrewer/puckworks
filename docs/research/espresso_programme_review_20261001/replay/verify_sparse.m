addpath(fileparts(mfilename('fullpath')));
addpath(fullfile(fileparts(mfilename('fullpath')),'source'));
fid=fopen('backend.txt','w'); fprintf(fid,'version=%s\node15s=%s\ncompiled=%s\n',version,which('ode15s'),which('__ode15__'));
features=__octave_config_info__('build_features'); fprintf(fid,'KLU=%d SUNLINSOL_KLU=%d\n',features.KLU,features.SUNDIALS_SUNLINSOL_KLU); fclose(fid);
assert(features.SUNDIALS_SUNLINSOL_KLU);
global FIXTURE_JAC_CALLS; FIXTURE_JAC_CALLS=0;
M=sparse(diag([1,0])); opt=odeset('Mass',M,'MStateDependence','none','Jacobian',@fixture_jacobian, ...
 'RelTol',1e-8,'AbsTol',1e-10,'Stats','on');
tout=linspace(0,5,501); profile on;
[t,y]=ode15s(@(t,y) [-y(1);y(1)+y(2)-1],tout,[1;0],opt);
profile off; prof=profile('info');
fid=fopen('fixture_profile.csv','w'); fprintf(fid,'function,calls,seconds\n');
wrapcalls=0;
for i=1:numel(prof.FunctionTable)
 p=prof.FunctionTable(i);
 if ~isempty(strfind(p.FunctionName,'jac')) || ~isempty(strfind(p.FunctionName,'ode15'))
  fprintf(fid,'%s,%d,%.17g\n',p.FunctionName,p.NumCalls,p.TotalTime);
  if ~isempty(strfind(p.FunctionName,'wrapjacfcn')); wrapcalls+=p.NumCalls; end
 end
end
fclose(fid);
err=max(max(abs(y-[exp(-t),1-exp(-t)]))); con=max(abs(sum(y,2)-1));
dlmwrite('sparse_fixture.csv',[t,y],'precision','%.17g');
result=struct('state_error',err,'constraint_residual',con,'jacobian_calls',FIXTURE_JAC_CALLS, ...
 'installed_wrapjac_calls',wrapcalls,'state_limit',1e-6,'constraint_limit',1e-8);
fid=fopen('sparse_fixture.json','w'); fprintf(fid,'%s\n',jsonencode(result)); fclose(fid);
assert(err<=1e-6 && con<=1e-8 && FIXTURE_JAC_CALLS>1 && wrapcalls>0);

% N=40 analytic derivative verification against ORIGINAL RHS calls.
d=define_parameters(); N=40; dx=1/(N-1); x=linspace(0,1,N); n=N+2*N*N;
p=[N dx d(9) d(3) d(4) d(1) d(2) d(10) d(5) d(6) d(7) d(12) d(8)];
A=linear_jacobian(p,x); M=build_mass(N,dx,x); Ms=sparse(M);
assert(isequal(full(Ms),M)); assert(nnz(Ms(1,:))==0 && nnz(Ms(N,:))==0);
fid=fopen('mass_N40.json','w'); fprintf(fid,'%s\n',jsonencode(struct('n',n,'nnz',nnz(Ms),'exact_equality',true,'zero_rows',[1 N]))); fclose(fid); clear M Ms;
idx=(1:n)'; states=zeros(n,4); states(:,1)=[zeros(N,1);ones(2*N*N,1)];
for c=2:4
 states(:,c)=.65+.3*sin(idx*.127+c).^2;
end
states(1:N,2)=1e-9*(1+x');
states(1:N,3)=.999-.0005*x';
states(1:N,4)=.15+.5*x';
for c=2:4
 states(N+(1:N)'*N,c)=.5+.4*x';
 states(N+N*N+(1:N)'*N,c)=.25+.25*cos(x'*3).^2;
end
rand('seed',731); directions=[sin(idx*.617),2*rand(n,1)-1,zeros(n,2)];
directions(1:N,3)=cos((1:N)'*.4);
directions([1;N;N+(1:N)'*N;N+N*N+(1:N)'*N],4)=1;
for j=1:4; directions(:,j)=directions(:,j)/max(abs(directions(:,j))); end
hvalues=[1e-3,1e-5,1e-7]; rows=[]; worst_best=0;
for c=1:4
 u=states(:,c); J=rhs_jacobian(0,u,p,x,A);
 for j=1:4
  v=directions(:,j); exact=J*v; errors=[];
  for h=hvalues
   approx=(RHS(0,u+h*v,p,x)-RHS(0,u-h*v,p,x))/(2*h);
   delta=abs(approx-exact); ae=max(delta); se=max(delta./(1+abs(exact)));
   rows(end+1,:)=[c j h ae se]; errors(end+1)=se;
  end
  worst_best=max(worst_best,min(errors(2:3)));
 end
end
fid=fopen('jacobian_differences.csv','w'); fprintf(fid,'state,direction,h,max_absolute,max_scaled\n'); fclose(fid);
dlmwrite('jacobian_differences.csv',rows,'-append','precision','%.17g');
% Independent complex-step differentiation of the unexpanded reaction polynomial.
G=@(l,s) p(8)*(1-l).*s.*(s-p(11)*l); surf_error=0;
for l=[0,1e-10,.3,.99999]
 for s=[.1,.7,1,1.8*l]
  analytical=[-p(8)*s*(s+p(11)-2*p(11)*l),p(8)*(1-l)*(2*s-p(11)*l)];
  numerical=[imag(G(l+1i*1e-25,s))/1e-25,imag(G(l,s+1i*1e-25))/1e-25];
  surf_error=max(surf_error,max(abs(analytical-numerical)));
 end
end
fid=fopen('jacobian_checks.json','w'); fprintf(fid,'%s\n',jsonencode(struct('worst_best_scaled',worst_best,'scaled_limit',1e-7,'surface_derivative_abs_error',surf_error,'surface_limit',1e-12,'checks',size(rows,1)))); fclose(fid);
assert(worst_best<=1e-7 && surf_error<=1e-12);
disp('SPARSE_FIXTURE_AND_JACOBIAN_CHECKS_PASS');
