"""Derived presentation comparisons, conditional on the saved on-target planet model."""
import json, math
from pathlib import Path
D=Path('analysis/validation-20261011/post/data')
k=json.loads((D/'kic5689121_key_numbers.json').read_text());m=json.loads((D/'kic5689121_model_numbers.json').read_text())
p=k['ephemeris']['period_d'][0];a=m['a_AU'];km=a*149597870.7
facts={
 'assumption':'Planet orbits the adopted host. Circular orbit for speed; no mass or composition inference.',
 'inputs':{'period_days':p,'a_AU':a,'radius_earth_range':m['radius_earth'],'distance_pc':k['target']['distance_pc']},
 'constants':{'AU_km':149597870.7,'c_km_s':299792.458,'earth_mean_radius_km':6371,'julian_year_days':365.25,'mercury_a_AU':0.387},
 'orbit_radius_km':km,'circular_orbit_speed_km_s':2*math.pi*km/(p*86400),
 'orbits_per_earth_year':365.25/p,'star_to_orbit_light_seconds':km/299792.458,
 'mercury_distance_fraction':a/0.387,
 'diameter_km_range':[2*6371*r for r in m['radius_earth']],
 'volume_earth_range':[r**3 for r in m['radius_earth']],
 'equilibrium_temperature_K':m['Teq_K_zero_albedo'],'equilibrium_temperature_C':m['Teq_K_zero_albedo']-273.15,
 'light_travel_years':k['target']['distance_pc']*3.261563777,
 'emission_epoch_CE_range':[y-k['target']['distance_pc']*3.261563777 for y in [2009,2013]],
 'stellar_angular_diameter_deg':m['star_angular_diam_deg'],
 'apparent_star_width_vs_sun':m['star_angular_diam_deg']/m['sun_angular_diam_deg'],
 'transit_fraction_range':[h/(p*24) for h in [2.1,2.4]],
 'unknown':['mass','density','gravity','composition','cloud colour','atmospheric structure','interior layer boundaries','rotation','moons','rings']}
Path('docs/derived/planet-comparisons.json').write_text(json.dumps(facts,indent=2)+'\n')
print(json.dumps({key:val for key,val in facts.items() if key not in ['inputs','constants','unknown']},indent=2))
