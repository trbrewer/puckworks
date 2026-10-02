clear all
% clf suppressed for headless execution
close all
clc

tic

plot_flag=0; % Uses figures 1-4
checkmass_flag=0; % Uses figure 5

N=40;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define the dimenionless parameters %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

dimensionlessparameters=define_parameters;
bet1=dimensionlessparameters(1);
bet2=dimensionlessparameters(2);
Ds1=dimensionlessparameters(3);
Ds2=dimensionlessparameters(4);
Q1=dimensionlessparameters(5);
Q2=dimensionlessparameters(6);
beta=dimensionlessparameters(7);
q=dimensionlessparameters(8);
Deff=dimensionlessparameters(9);
K=dimensionlessparameters(10);
alpha=dimensionlessparameters(11);
phis=dimensionlessparameters(12);

dx=1/(N-1);
x=linspace(0,1,N);

T_end=10;
main_times=linspace(0,T_end,20001); early_log=logspace(-9,log10(5e-6),401); extra_times=[early_log(1:end-1),linspace(5e-6,0.02,4000)]; near_indices=round(extra_times/0.0005)+1; extra_times=extra_times(abs(extra_times-main_times(near_indices))>1e-13); tout=sort([main_times,extra_times]); assert(all(diff(tout)>1e-13));

cl0=zeros(N,1);
u10=ones(N,1);
u20=ones(N,1);

disp(['The value of D_eff is ' num2str(Deff)])
disp(['The value of D_s1 is ' num2str(Ds1)])
disp(['The value of D_s2 is ' num2str(Ds2)])
disp(['The value of Q_1 is ' num2str(Q1)])
disp(['The value of Q_2 is ' num2str(Q2)])
disp(['The value of b_et1 is ' num2str(bet1)])
disp(['The value of b_et2 is ' num2str(bet2)])
disp(['The value of K is ' num2str(K)])
disp(['The value of beta is ' num2str(beta)])
disp(['The value of nu is ' num2str(q)])

% Concatenate the initial data
u0=[cl0; u10];
for i=1:N-1
    u0=[u0; u10];
end
for i=1:N
    u0=[u0; u20];
end

% Build the mass matrix
M=build_mass(N,dx,x);

% Solve the problem
p=[N dx Deff Ds1 Ds2 bet1 bet2 K Q1 Q2 beta phis q];
monitor_init(p,x);
M_original=M; M_sparse=sparse(M_original);
assert(isequal(full(M_sparse),M_original));
assert(nnz(M_sparse(1,:))==0 && nnz(M_sparse(N,:))==0);
fid=fopen('mass_check.json','w'); fprintf(fid,'%s\n',jsonencode(struct('exact_equality',true,'n',size(M,1),'nnz',nnz(M_sparse),'algebraic_rows',[1 N]))); fclose(fid);
M=M_sparse; clear M_original M_sparse;
options=odeset('Mass',M,'Stats','on','OutputFcn',@progress_output,'MStateDependence','none','Jacobian',@counted_jacobian,'RelTol',1e-07,'AbsTol',1e-09);
params=[N dx Deff Ds1 Ds2 bet1 bet2 K Q1 Q2 beta phis q];
[t,u]=ode15s(@counted_rhs,tout,u0,options);
finish_monitor();

% Pull out the concentration at the exit
c_exit=zeros(length(tout),1);
for i=1:length(tout)
    c_exit(i)=u(i,N);
end

% Do the post-processing to find the EY
extract=trapz(tout,c_exit);
disp('----------------------------')
disp([num2str(1e2*q*beta*extract/phis) '% of the coffee was extracted'])
disp(['The EY was ' num2str(1e2*alpha*q*beta*extract/phis) '%'])
comp_time=toc;
disp(['The computation took ' num2str(comp_time) ' seconds'])
disp('----------------------------')

if plot_flag==1
    plotresults(tout,u,N,x)
end
if checkmass_flag==1
    checkmass(tout,u,x,params)
end
