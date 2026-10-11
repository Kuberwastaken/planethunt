# Independent check

A separate agent rewrote the key measurements from scratch (these scripts), without reading the
main analysis code, and compared against the claims in `../README.md`.

| Claim | Verdict | Independent numbers |
|---|---|---|
| KIC 5689121 depth ~2,100–2,400 ppm at > 15σ | Pass, with caveat | 1,958 ± 46 ppm for a plain 2.2 h box; 1,830–2,430 ppm across methods; 11–22σ against measured scatter (43σ formal) |
| No overlap with Kepler-169 e | Pass | Closest approach 67.3 h; fold on Kepler-169 e ephemeris 80 ± 39 / 14 ± 45 ppm |
| 2 of 1,736 inverted nulls as strong | Pass | KIC 8701308 (4.254 d) and KIC 5283912 (8.785 d); 1,736 source_ids (1,648 unique KICs) |
| TIC 309780779 late half on frozen ephemeris | Pass on transit; timing resolution limited | Offset +4 min (−12 to +11 min); late depth 382–444 ppm at 9–10σ |
| TIC 309780779 phase-0.5 depth ≈ 0 | Pass | −44 ± 30 ppm (−23 to −48 across variants); sectors ≥ 61 alone −94 ± 44 ppm (a 2σ brightening, not an eclipse) |

Paths inside the scripts point at the session workspace; adjust to your merged archive location.
