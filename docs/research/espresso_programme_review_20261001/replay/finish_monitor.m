function finish_monitor()
global CAMMON;
write_monitor('monitor.json'); fflush(CAMMON.progress); fclose(CAMMON.progress);
end
