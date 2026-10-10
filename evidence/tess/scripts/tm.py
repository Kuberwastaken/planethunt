import sys,time; sys.path.insert(0,sys.argv[1])
import env, lcsearch as L
lc,_,_=L.reject_bad_sectors(L.load_star(370612437)); c=L.bin_lc(L.clean(lc))
t=time.time(); sg,_=L.bls_search(c,1.0); print(sys.argv[1],round(time.time()-t,1),[(round(s['period'],4),round(s['snr'],1),round(s['sde'],1)) for s in sg])
