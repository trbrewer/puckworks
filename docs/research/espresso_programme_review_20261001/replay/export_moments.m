% Instrumentation after the source solve; does not alter its state or equations.
% Save complete spatial inventory moments at every output, plus endpoint/bracket
% states for an independent Python check, instead of a large full-state dump.
assert(length(t)==length(tout) && max(abs(t(:)-tout(:))) < 1e-10);
assert(all(isfinite(u(:))));
edges = [0, (x(1:end-1)+x(2:end))/2, 1];
radial_weights = diff(edges.^3); % normalized spherical control-volume fractions
history = zeros(length(t), 12);
for ii=1:length(t)
    cl = u(ii,1:N);
    f = reshape(u(ii,N+1:N+N*N),N,N);
    b = reshape(u(ii,N+N*N+1:end),N,N);
    fine_mean = trapz(x,radial_weights*f);
    coarse_mean = trapz(x,radial_weights*b);
    grad_in = (-1.5*cl(1)+2*cl(2)-0.5*cl(3))/dx;
    grad_out = (0.5*cl(end-2)-2*cl(end-1)+1.5*cl(end))/dx;
    g1 = trapz(x,K*(1-cl).*f(end,:).*(f(end,:)-beta*cl));
    g2 = trapz(x,K*(1-cl).*b(end,:).*(b(end,:)-beta*cl));
    history(ii,:) = [t(ii),trapz(x,cl),fine_mean,coarse_mean,cl(end), ...
                    q*cl(1)-Deff*grad_in, -Deff*grad_out, g1,g2, ...
                    min(u(ii,:)),max(u(ii,:)),cl(1)];
end
dlmwrite('history.csv',history,'precision','%.17g');
snapshot_indices = unique([1,find(t<=1,1,'last'),find(t>=1,1,'first'),length(t)]);
snapshot_u = u(snapshot_indices,:);
backend_version = version;
author_reported_EY = 100*alpha*q*beta*extract/phis;
initial_rhs = RHS(0,u0,params,x);
initial_algebraic_residual = max(abs(initial_rhs([1 N])));
assert(initial_algebraic_residual <= 1e-12);
% Supported file formats for independent scipy.io.loadmat reduction.
if exist('OCTAVE_VERSION','builtin')
    save('-mat7-binary','snapshots.mat','snapshot_indices','snapshot_u','x','N', ...
         'params','dimensionlessparameters','backend_version','author_reported_EY', ...
         'initial_algebraic_residual','comp_time');
else
    save('snapshots.mat','snapshot_indices','snapshot_u','x','N','params', ...
         'dimensionlessparameters','backend_version','author_reported_EY', ...
         'initial_algebraic_residual','comp_time','-v7');
end
