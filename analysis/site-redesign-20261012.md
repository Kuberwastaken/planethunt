# Public website rebuild — 12 October 2026

This is a presentation change. Scientific status is still the 11 October validation snapshot.
No original measurements, source archives, or evidence-pack checksums were changed.

The site now leads with the candidate and a real Pan-STARRS image, then progresses through
observations, sky context, vetting, conditional false-positive modelling, physical inferences,
other search outcomes, follow-up, and open evidence. Detailed diagnostics and original dated
sections remain available in expandable sections.

## Data and science handling

- The dynamic transit plot reads saved 15-minute bins and a sampled smooth transit model.
- The full light-curve view includes all 46,523 saved detrended cadences; it discloses points
  outside its plotted vertical range and links the complete CSV. Quarter filters use recorded
  quarter values only.
- The event view explicitly uses the 74-event / 23 reserved-quarter export, distinct from the
  strict original 70 / 22 selection. A full-baseline display is not a new blind holdout.
- FPP is described as conditional modelling. Hypothetical imaging remains visibly hypothetical;
  the baseline scenario table remains labelled as baseline when changing the what-if control.
- The radius, orbit, insolation and equilibrium temperature comparisons are conditional on the
  assumed host. Reflectivity changes a simple equilibrium model, not measured weather.
- The estimated light-emission epoch is around 1040 CE using the actual 2009–2013 observations
  and the approximate 298 pc distance, rather than subtracting travel time from today's year.
- The 1,736 null searches are source searches (1,648 unique KICs), not all independent unique stars.
- Season 3's two-event pixel result is qualified rather than being presented as strong localization.

## Images and charts

Fifteen SVG diagnostics are built from saved outputs, plus code-native scale comparisons.
The added Lyra locator uses the approximate coordinates in the original `post_where.py`.
Pan-STARRS and DSS2 raw cutouts are reused without changing their pixels. Clean 2MASS and
AllWISE renders were fetched from CDS hips2fits at the existing centre and field size, with
parameters and attribution recorded in `docs/sky/SOURCES.json`. Catalogue-position markers,
scale bars and north/east labels are rendered separately as SVG. The original registered
image panels are retained for inspection. Coarse surveys do not resolve every marked source.

## Verification

- Offline chart and page rebuilds are deterministic; JavaScript syntax and `git diff --check` pass.
- Checked all 114 page link/asset references for local existence or valid in-page targets,
  unique HTML IDs, SVG XML, and image alternatives. This does not claim every external service
  is reachable or its catalogue state is freshly verified.
- Compared the compact light-curve export against every original CSV row; verified event/bin
  counts, Gaia identifier string precision, and PNG file signatures.
- Browser checked at 320, 390, 768 and 1440 CSS-pixel widths; no document horizontal overflow.
- Exercised chart views, reserved-quarter filtering, quarter selection, survey switching,
  enlargement/Escape dismissal, hypothetical/available-evidence switching, temperature updates,
  file search (including empty results), archive filtering and pagination.
- Browser console showed no errors or warnings in the exercised flows.

The page remains static and compatible with repository-root GitHub Pages at `/planethunt/`.
This local rebuild does not itself publish or change the existing remote site.
