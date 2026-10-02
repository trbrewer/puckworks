function f=counted_rhs(t,u)
global CAMMON;
a=tic(); f=RHS(t,u,CAMMON.params,CAMMON.x); cost=toc(a);
CAMMON.rhs_calls+=1; CAMMON.rhs_seconds+=cost;
CAMMON.rhs_max_trial_time=max(CAMMON.rhs_max_trial_time,t);
w=toc(CAMMON.clock);
if w-CAMMON.last_flush_wall>=5
 fprintf(CAMMON.progress,'rhs_trial,%.17g,%.8g,%d,%d,%.8g,%.8g,NaN,NaN\n',t,w,CAMMON.rhs_calls,CAMMON.jac_calls,CAMMON.rhs_seconds,CAMMON.jac_seconds);
 fflush(CAMMON.progress); CAMMON.last_flush_wall=w;
 fprintf('RHS_TRIAL t_hat=%.9g wall=%.3f rhs=%d jac=%d\n',t,w,CAMMON.rhs_calls,CAMMON.jac_calls); fflush(stdout);
end
end
