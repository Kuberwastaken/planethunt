# From archival candidate to a defensible planet claim

Prepared 12 October 2026. This is a scientific collaboration and observing brief, not an approved proposal or a promise of confirmation.

**Second-pass update:** Read [the subsequent archive results](../archive-exhaustion-20261012/README.md) before using this brief. HST/JWST footprint checks now succeeded; new TGLC, ZTF, PTF, NEOWISE and CFHT data were examined. The exact star also occurs in the Barber et al. 2022 MELANGE-3 candidate list, without a confirmed age or membership. Its authors are relevant scientific-review contacts. The new PRF pixel injections also show why TESS has weak rejection power: an assumed 2,400 ppm dip on the target gives about 987 ppm in a 1.5-pixel aperture, versus 1,294 ppm off-phase scatter. This is conditional sensitivity, not completeness.

## The question to answer

The Kepler transit signal survives the existing holdout, pixel, contamination and timing checks. The largest remaining model branch is a planet transiting an unresolved bound companion rather than the adopted M dwarf. Existing survey images do not exclude that configuration. We need to identify the host, constrain hidden stars, and independently recover the transit.

**An AO image is a constraint on stellar companions, not a photograph of the planet.** Imaging alone may not validate the system: the repository's explicitly hypothetical contrast curve gave FPP ≈0.02694, still above its 0.015 threshold. The current measured-data FPP remains ≈0.06885. Statistical validation, independent transit recovery and a dynamical mass measurement are different achievements.

## Target card

| Field | Value / qualification |
|---|---|
| Target | KIC 5689121 = TIC 120686465 = Gaia DR3 2103792461826460288 |
| ICRS position used in analysis | RA 285.907827°, Dec +40.941988°; 19h 03m 37.878s, +40° 56′ 31.157″ |
| Gaia G | 16.2824 mag |
| 2MASS J / H / Ks | 13.883 ±0.024 / 13.213 ±0.026 / 12.969 ±0.028 mag; catalogue values, possible unresolved blending |
| Adopted stellar estimates | ~3633 K, ~0.51 R☉, ~0.505 M☉; re-fit in a joint stellar analysis if new constraints warrant |
| Fresh Gaia parallax | 3.40648 ±0.03973 mas, before zero-point correction |
| Period | 13.7694482515 d; saved marginal uncertainties −0.0000637143 / +0.0000660202 d |
| Reference mid-transit | BJD_TDB 2455630.245430646; saved marginal uncertainties −0.00196885 / +0.00200801 d |
| Depth and duration | ~0.2–0.24%, extraction-dependent; ~2.1–2.4 h |
| Bright optical neighbour | KIC 5689116 / TIC 120686466 / Gaia DR3 2103792427466721792, 7.1″ west, G≈15.5 |
| Neighbour position | RA 285.90521895334°, Dec +40.94207048408° |
| Confusable nearby system | Kepler-169 / KOI-505, ~4.4′ away; similar-period planet already timing-tested |
| Infrared archive result | Target ~2.1 mJy at 3.6 μm, ~1.3 mJy at 4.5 μm; out-of-transit Spitzer exposures |

Use the Gaia proper motion and reference epoch when preparing acquisition coordinates; the positions above reproduce this analysis, not an observing-date astrometric solution. Propagate the joint ephemeris posterior for scheduling. The marginal period error alone accumulates to roughly 40 minutes by 2027. A precise UTC schedule also requires the barycentric correction for the observatory. Do not book a narrow transit window using the displayed central epoch alone.

## Observations and decision points

1. **Independent scientific review and a joint host-star fit.** Give a collaborator the original light curves, neighbour controls, pixel tests, ephemeris posterior and the new audit. Reconcile the Gaia distance with the adopted stellar parameters. Do not treat normal RUWE as a binary veto, or the Spitzer colour as a deblended spectrum of a single star. A joint SED/stellar fit must allow unresolved multiplicity and correlated catalogue inputs.
2. **Near-infrared adaptive-optics imaging.** Ask a Keck/NIRC2 observer to assess Ks≈13 feasibility, guide-star requirements and exposure time. The nearby G≈15.5 star is a possible guide-star lead, not proof of a suitable R-band tip-tilt magnitude. Seek a calibrated detection/completeness curve over approximately 0.05–2″, with the actual achieved inner working angle, filter and method. Ideally obtain a second band for any detected companion, plus separation, position angle and flux ratio. Acquisition coverage must account for the known 7.1″ neighbour. A non-detection needs injection/recovery or the team's validated contrast-curve procedure. A detected close companion redirects the analysis toward host identification rather than an automatic planet claim.
3. **Recover a full transit with resolved ground photometry.** Assess a northern 1–2 m class or larger facility with a suitably sensitive red band and seeing that separates the 7.1″ pair. This is a feasibility starting point, not an exposure-time estimate. Ask for in-transit precision and systematics calculations at this brightness; observe the target and neighbour simultaneously. Cover ingress, egress, timing uncertainty and at least ~1 hour of baseline on both sides. A second band can constrain strongly chromatic blends but an achromatic dip alone does not establish the host or rule out all false positives. A second event protects against a single-night systematic and refreshes the ephemeris.
4. **Reconnaissance spectroscopy if feasible.** Look for composite spectra, a spectroscopic companion or large velocity changes and refine stellar properties. This faint M dwarf may require substantial telescope time. No stellar mass–radius relation predicts a measured planet mass; evaluate precision RV feasibility with an instrument specialist before proposing a dynamical confirmation programme.
5. **Re-run validation with actual constraints.** Incorporate the measured contrast curve, any companion photometry, spectra and refreshed transit fit in a documented model; examine model adequacy and prior sensitivity. Avoid double-counting Gaia or overlapping survey measurements. Report the host ambiguity separately from whether some planetary interpretation is probable. Publish a revised probability only after the inputs and inference are reproducible and reviewed.

## Who to approach, in order

| Contact | Why this person / role | Specific request |
|---|---|---|
| **Madyson Barber — madysonb@live.unc.edu; Andrew Mann — awmann@unc.edu** | Authors of the exact-star MELANGE-3 catalogue match; contacts on [Barber’s site](https://madysonb.github.io/) and [Mann’s site](https://andrewwmann.com/) | First resolve the Table 5 Kepler=Y association: which KIC/file was searched, whether the 13.77-day signal was examined, and what evidence supports membership. Approach as a data/provenance question; do not presume the star is young or the signal new. |
| **David Ciardi — ciardi@ipac.caltech.edu** | IPAC/NExScI; his [official profile](https://www.ipac.caltech.edu/science/staff/david-ciardi) lists planetary systems with multiple stars as his research interest | AO/host-identification collaborator or referral: review the unresolved-host problem and assess whether an experienced Keck AO team could take it on |
| **Elise Furlan — furlan@ipac.caltech.edu** | [IPAC profile](https://www.ipac.caltech.edu/science/staff/elise-furlan); stellar characterization and exoplanet host work | An alternative scientific contact for stellar/dilution analysis, not a simultaneous duplicate request to the same group |
| **Karen Collins — contact through her [CfA profile](https://www.cfa.harvard.edu/people/karen-collins)** | Ground-based transit follow-up and TFOP SG1 leadership | Advice or referral for red-band photometry of a faint northern Kepler candidate. This is not a TOI and has no automatic TFOP allocation |
| **NASA-Keck programme — KeckCFP@ipac.caltech.edu** | [Official call](https://nexsci.ipac.caltech.edu/missions/KeckSolicitation/) | Administrative eligibility/cycle questions once a scientific collaboration is in place; not a substitute for an observing PI |

A referral from the existing scientific contact is the least burdensome first step. No messages have been sent by this analysis, and no person's participation or telescope access is assumed.

## Time allocation route

The official **2027A NASA-Keck call closed on 10 September 2026**. Its PI must have a principal affiliation at a US institution; co-investigators may have other nationalities and affiliations, subject to the call's stated restrictions. An India-based undergraduate can therefore contribute as a co-investigator with an eligible, scientifically involved PI. The next open cycle must be checked when announced. Institutional access or an already-approved programme would require the collaborator's genuine eligibility and programme compatibility; neither is assumed.

The [NIRC2 instrument page](https://www2.keck.hawaii.edu/inst/nirc2/) and the call's current AO notes are the starting points for an observer's feasibility assessment. The 2027A call lists Keck II natural-guide-star AO for guide stars brighter than R=15 and laser-guide-star AO availability. Do not substitute Gaia G for R or assume that “available” removes guide-star and scheduling requirements.

## What remains possible without new telescope time

The two audit packs contain reproducible Spitzer reductions, ten-sector TESS aperture analysis, six-sector TGLC target/neighbour checks, conditional pixel injections, ZTF target/neighbour fits, PTF and NEOWISE timing checks, CFHT registration/saturation diagnostics, and the relevant catalogue/footprint searches. The current MAST browser UI and ESA footprint service resolved the earlier HST/JWST service gap: no exact-target footprint was returned. Four Robo-AO survey catalogues also returned no match within 30″.

Remaining work is substantive modelling or access to different data: recover a trustworthy unsaturated CFHT product if one exists; calibrate a time-dependent TESS scene and blind-search completeness; fit the stellar SED with extinction and multiplicity; and reconcile the THYME light-curve identity. The 62 IRSA dataset matches include repeated releases and coarse maps, not 62 useful independent host constraints. Proprietary and unindexed observations remain unverified. This audit does not establish that every possible archive product is exhausted.

The strongest new next step is the THYME provenance question, followed by an experienced AO collaborator’s review. Neither requires presenting the candidate as confirmed or waiting for every possible model variant. Use the [updated draft reply](../archive-exhaustion-20261012/reply-to-steve.txt); no outreach has been sent.
