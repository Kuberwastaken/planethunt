# Publication snapshot — 13 October 2026 (Asia/Kolkata)

This package revision accompanies `evidence-20261013-r2`. The GitHub publication timestamp is recorded in UTC and can fall on 12 October. The prior evidence release was already public on 10 October 2026 at 15:41:31 UTC. Neither timestamp proves priority or that the signal is a previously unknown planet.

## Status

- Kuber Mehta is the sole listed manuscript author.
- The RNAAS note is a draft for human review, not submitted, accepted or peer reviewed.
- No Zenodo DOI has been issued at packaging time. The GitHub integration is enabled. Original code is MIT; original text, figures and analysis products are CC BY 4.0; third-party terms remain in force (see `LICENSE` and `SOURCES.md`).
- The signal remains unvalidated. The modelled FPP is 0.06885, with unresolved host ambiguity and provisional novelty.

## Files and reproduction

`manuscript.json` is the text source; `build_manuscript.py` produces `rnaas.tex`, `rnaas.txt`, `rnaas-review.pdf` and `word-count.json`. The editable journal source uses AASTeX 7. The review PDF is separately typeset with ReportLab, not a compiled AASTeX proof. Compile the final AASTeX source in the journal portal or Overleaf and inspect it before submission.

`make_figure.py` renders one two-panel scientific figure from preserved numeric inputs. It does not refit the data. `figure_sources.json` records input paths and SHA-256 hashes. Run from a Python environment containing numpy/matplotlib; the manuscript builder requires ReportLab. Run both scripts from any directory (they resolve paths relative to this package).

`claim-sources.json` points reviewers to the saved evidence. `bulk-data-manifest.json` links and hashes the large original archives in the 10 October release. The repository source archive contains the tracked evidence and website; it does not include externally hosted bulk assets simply because they are linked.

## Before RNAAS submission

1. Author metadata supplied: Independent researcher, New Delhi, India; kuberhob@gmail.com; ORCID 0009-0003-1379-7856.
2. Author reads and verifies the text, claims, figure, citations, attribution and AI disclosure. Resolve the THYME light-curve identity if possible; otherwise retain the explicit provisional-novelty language.
3. Replace the release citation with the verified version DOI if one is issued. Never insert a guessed DOI.
4. Compile `rnaas.tex` with AASTeX 7, inspect the generated PDF, then recount after any changes. Current draft: 1,196 words including 124-word abstract and one two-panel figure. Metadata additions may change the count.
5. Submit through https://aas.msubmit.net/ with journal Research Notes of the AAS. Review the portal's actual declarations and publication agreement; do not fabricate authorship, originality, funding or conflict answers. `cover-letter.txt` is a proposed cover note, not a sent message.

## Official guidance checked 13 October 2026 (local date)

- https://journals.aas.org/research-note-preparation-guidelines — 1,500-word total; abstract up to 150 words; one figure or table (multi-panel figure allowed); no line numbers; sole-author first person.
- https://journals.aas.org/research-notes/ — editorial moderation, not peer review; acceptance is not guaranteed.
- https://journals.aas.org/author-llm-guidelines — human accountability and disclosure of material AI use.
- https://journals.aas.org/submission/ — official portal and author preparation checklist.
- https://help.zenodo.org/docs/github/enable-repository/ — connect GitHub and enable the repository before automatic ingestion of new releases.
- https://help.zenodo.org/docs/github/describe-software/ — `.zenodo.json` takes precedence over `CITATION.cff` if both exist.
- https://help.zenodo.org/docs/github/archive-software/github-upload/ — processing can take time; verify the finished record and DOI.

If the GitHub release precedes integration setup, preserve that release and manually deposit its exact archived snapshot in Zenodo, or create a subsequent properly versioned release after enabling integration. Do not delete and recreate the historical release to manufacture an earlier DOI date.
