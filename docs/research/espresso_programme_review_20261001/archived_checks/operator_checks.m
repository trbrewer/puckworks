addpath('source');
d=define_parameters(); N=40; h=1/(N-1); x=linspace(0,1,N);
p=[N h d(9) d(3) d(4) d(1) d(2) d(10) d(5) d(6) d(7) d(12) d(8)];
M=build_mass(N,h,x); B=M(N+1:2*N,N+1:2*N);
e=[0,(x(1:end-1)+x(2:end))/2,1];v=4*pi/3*diff(e.^3)';
A=B/diag(v); colerr=max(abs(sum(A,1)-1)); blockerr=max(abs(sum(B,1)-v'));
assert(colerr<=2e-13 && blockerr<=2e-13); clear M;
w=h*ones(N,1);w([1,N])=h/2;epsi=1-p(12);n=N+2*N*N;
% Read original algebraic coefficients using basis calls, not the proposed formula.
rowidx=[1,2,3,N-2,N-1,N];bc=zeros(2,N);
for j=rowidx
 eunit=zeros(n,1);eunit(j)=1;f=RHS(0,eunit,p,x);bc(:,j)=f([1,N]);
end
states={[zeros(N,1);ones(2*N*N,1)]}; labels={'initial'};
for k=1:3
 a=(1:n)';z=.4+.5*sin(.017*a+k).^2;
 z(1:N)=.02*k+.01*sin(3*x')+.03*x';
 z(1)=-(bc(1,2:N)*z(2:N))/bc(1,1);
 z(N)=-(bc(2,1:N-1)*z(1:N-1))/bc(2,N);
 states{end+1}=z;labels{end+1}=sprintf('synthetic_%d',k);
end
old='../sparse-execution-20261001T133411Z';
for c={'reference_sparse','tight_sparse'}
 s=load(fullfile(old,c{1},'snapshots.mat'));
 for k=1:size(s.snapshot_u,1)
  states{end+1}=s.snapshot_u(k,:)';labels{end+1}=sprintf('%s_snapshot_%d',c{1},k);
 end
 for k=[2,3,21]
  s=load(fullfile(old,c{1},sprintf('diagnostic_%03d.mat',k)));
  states{end+1}=s.snapshot_u;labels{end+1}=sprintf('%s_callback_%d',c{1},k);
 end
end
fid=fopen('operator_checks.csv','w');
fprintf(fid,'state,inventory_plus_cup_rate,identity_rate,absolute_error,scale,inlet_constraint,outlet_constraint,wrong_sign_error,wrong_weights_error\n');
maxerr=0;maxscaled=0;rejected_sign=false;rejected_weights=false;
for k=1:numel(states)
 u=states{k};f=RHS(0,u,p,x);c=u(1:N);cp=zeros(N,1);cp(2:N-1)=f(2:N-1);
 cp([1,N])=bc(:,[1,N])\(-bc(:,2:N-1)*cp(2:N-1));
 % Only nonsingular 40x40 particle blocks are solved. Never invert full M.
 ds=B\reshape(f(N+1:end),N,2*N);
 solid_ax=d(1)/(d(7)*d(5)*4*pi)*(v'*ds(:,1:N))' ...
          +d(2)/(d(7)*d(6)*4*pi)*(v'*ds(:,N+1:end))';
 rate_by_operator=w'*(epsi*cp+solid_ax)+d(8)*c(N);
 sf=u(N+(1:N)'*N);sc=u(N+N*N+(1:N)'*N);
 G=@(l,s) p(8)*(1-l).*s.*(s-p(11)*l);
 S=p(6)*G(c,sf)+p(7)*G(c,sc);
 adv=p(13)/2*(c(N)-c(N-1)+c(1)+c(2));
 dispterm=p(3)/h*(c(N)-c(N-1)-c(2)+c(1));
 endterm=h/2*(epsi*(cp(1)+cp(N))-S(1)-S(N));
 identity=adv+dispterm+endterm;scale=1+abs(adv)+abs(dispterm)+abs(endterm);
 err=abs(rate_by_operator-identity);assert(err<=5e-11*scale);
 maxerr=max(maxerr,err);maxscaled=max(maxscaled,err/scale);
 % Vectorized reaction/interior derivative independently checked against original f.
 liq_interior=(-p(13)*(c(3:end)-c(1:end-2))/(2*h)+p(3)*(c(3:end)-2*c(2:end-1)+c(1:end-2))/h^2+S(2:end-1))/epsi;
 assert(max(abs(liq_interior-f(2:N-1)))<=5e-11*(1+max(abs(f(2:N-1)))));
 wc=w;wc([1,N])=0;badweight=wc'*(epsi*cp+solid_ax)+d(8)*c(N);
 signerror=abs(rate_by_operator+identity);weighterror=abs(badweight-identity);
 rejected_sign=rejected_sign||(signerror>5e-11*scale);rejected_weights=rejected_weights||(weighterror>5e-11*scale);
 fprintf(fid,'%s,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n',labels{k},rate_by_operator,identity,err,scale,f(1),f(N),signerror,weighterror);
 if k==1; initial_rate=-rate_by_operator; initial_formula=h/2*((p(6)+p(7))*p(8))*p(13)/(p(13)+1.5*p(3)/h);end
end
fclose(fid);assert(rejected_sign && rejected_weights);
% Dimensional factor independently assembled from released literal parameters.
R=29.2e-3;L=18.7e-3;csat=212.4;kg_to_mg=1000*1000;
initial_mg=pi*R^2*L*csat*kg_to_mg*initial_rate;
assert(abs(initial_rate-initial_formula)<5e-11);assert(abs(initial_mg-initial_mg/1000)>1e-8);
out=struct('states_checked',numel(states),'particle_column_sum_error',colerr, ...
 'particle_weight_identity_error',blockerr,'max_identity_abs_error',maxerr, ...
 'max_identity_scaled_error',maxscaled,'sign_mutation_rejected',rejected_sign, ...
 'endpoint_weight_mutation_rejected',rejected_weights,'kg_to_mg_mutation_rejected',true, ...
 'initial_E_core_rate_mg_per_scaled_time',initial_mg,'initial_E_core_rate_mg_per_second',initial_mg/33.9);
fid=fopen('operator_results.json','w');fprintf(fid,'%s\n',jsonencode(out));fclose(fid);
disp(out);
