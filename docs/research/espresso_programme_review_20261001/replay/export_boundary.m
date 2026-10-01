% Raw returned-solution components missing from the previous moment exporter.
% No new ODE equations, rates, quadrature or inventory weights here.
assert(size(u,1)==numel(t) && size(u,2)==N+2*N*N);
cols=[1,2,3,N-2,N-1,N,2*N,N*N+2*N,N*N+N,2*N*N+N];
boundary_history=[t(:),u(:,cols)];
fid=fopen('boundary_history.csv','w');
fprintf(fid,'t_hat,c1,c2,c3,cNm2,cNm1,cN,sfine1,scoarse1,sfineN,scoarseN\n');fclose(fid);
dlmwrite('boundary_history.csv',boundary_history,'-append','precision','%.17g');
