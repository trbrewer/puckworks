function write_monitor(filename)
global CAMMON;
s=rmfield(CAMMON,{'clock','A','params','x','progress'}); s.wall_seconds=toc(CAMMON.clock);
f=fopen(filename,'w'); fprintf(f,'%s\n',jsonencode(s)); fclose(f);
end
