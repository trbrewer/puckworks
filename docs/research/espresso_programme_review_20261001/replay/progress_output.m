function stop=progress_output(t,y,flag)
global CAMMON;
stop=false;
if strcmp(flag,'done'); return; end
if strcmp(flag,'init'); t=t(1); y=y(:,1); end
for j=1:numel(t)
 tt=t(j); yy=y(:,j); w=toc(CAMMON.clock);
 CAMMON.callback_calls+=1; CAMMON.callback_last_time=tt;
 fprintf(CAMMON.progress,'output_callback,%.17g,%.8g,%d,%d,%.8g,%.8g,%.8g,%.8g\n',tt,w,CAMMON.rhs_calls,CAMMON.jac_calls,CAMMON.rhs_seconds,CAMMON.jac_seconds,min(yy),max(yy));
 if tt-CAMMON.last_snapshot_time>=.25 || w-CAMMON.last_flush_wall>=5 || strcmp(flag,'init')
  CAMMON.snapshots+=1; CAMMON.last_snapshot_time=tt; CAMMON.last_flush_wall=w;
  snapshot_t=tt; snapshot_u=yy;
  save('-mat7-binary',sprintf('diagnostic_%03d.mat',CAMMON.snapshots),'snapshot_t','snapshot_u');
  fflush(CAMMON.progress);
  fprintf('OUTPUT_CALLBACK t_hat=%.9g wall=%.3f rhs=%d jac=%d\n',tt,w,CAMMON.rhs_calls,CAMMON.jac_calls); fflush(stdout);
  write_monitor('monitor_latest.json');
 end
end
end
