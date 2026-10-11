import json, textwrap, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
exec(open('/root/ph/post/post_figs.py').read().split('# ------------------------------------------------------------------ data')[0])
S=json.load(open('/root/ph/work/tri/fpp_summary.json'))
fig=plt.figure(figsize=(14,8.2)); title(fig,'How sure are we? Candidate, not confirmed','What the checks rule out so far, and what still needs a telescope.')
PASS,OPEN='✓','•'
left=[('Repeats on schedule','70 transits in 13 Kepler quarters; still present (5.8σ) in the last 4 quarters, held out of the search'),
      ('Not a neighbouring planet','Kepler-169 e has almost the same period, but no transit ever lines up (closest 67 h apart; periods differ by 32σ)'),
      ('Light lost is on this star','Raw-pixel centroids point to it; every other Gaia star within 30″ rejected (Δχ² ≥ 934)'),
      ('Not the brighter star next door','KIC 5689116 shows 24 ± 41 ppm at transit; it would need ≈ 1,100 ppm'),
      ('No eclipsing-binary signature','Odd/even depths agree (0.6σ); no secondary eclipse (17 ± 59 ppm); shape fits the star\'s density')]
right=[('False-positive probability ≈ %.2f'%S['kepler G21']['FPP_mean'],'TRICERATOPS, mean of 4 runs. Validation needs < 0.015'),
       ('Main loophole','A planet around an unseen companion star (STP ≈ %.2f)'%S['kepler G21']['mean_probs']['STP']),
       ('Needs','High-resolution (AO) imaging + Gaia-based companion limits; multi-colour transit'),
       ('Not a unique detection strength','≈ 2 of 1,736 inverted null searches score as high; the case rests on vetting')]
fig.text(0.045,0.80,'RULED OUT / PASSED',fontsize=11,weight='bold',color=BLUE)
for i,(h,t_) in enumerate(left):
    y=0.74-i*0.13; fig.text(0.045,y,PASS,fontsize=18,color=BLUE,va='top'); fig.text(0.075,y,h,fontsize=14,color=INK,va='top',weight='bold')
    fig.text(0.075,y-0.042,textwrap.fill(t_,62),fontsize=10.5,color=INK2,va='top',linespacing=1.35)
fig.text(0.56,0.80,'STILL OPEN',fontsize=11,weight='bold',color=ORANGE)
for i,(h,t_) in enumerate(right):
    y=0.74-i*0.14; fig.text(0.56,y,OPEN,fontsize=18,color=ORANGE,va='top'); fig.text(0.59,y,h,fontsize=14,color=INK,va='top',weight='bold')
    fig.text(0.59,y-0.042,textwrap.fill(t_,52),fontsize=10.5,color=INK2,va='top',linespacing=1.35)
foot(fig,'All numbers from Kepler Bonus PSF photometry and Kepler target pixel files. Full methods and scripts: github.com/Kuberwastaken/planethunt')
fig.savefig(OUT+'post_04_status.png',dpi=150); plt.close(fig); print('ok')
