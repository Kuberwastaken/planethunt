# Publication snapshot — 13 October 2026 (Asia/Kolkata)

This package revision accompanies `evidence-20261013-r2`. The GitHub publication timestamp is recorded in UTC and can fall on 12 October. The prior evidence release was already public on 10 October 2026 at 15:41:31 UTC. Neither timestamp proves priority or that the signal is a previously unknown planet.

## Status

- Kuber Mehta is the sole listed manuscript author.
- The RNAAS note was submitted as **AAS82222**, revision 0, on 13 October 2026 (Asia/Kolkata). The portal displays `12-Oct-2026 16:20:10` without a timezone label. The author subsequently received a rejection dated **13 October 2026**. See the [post-decision audit](../../analysis/editorial-audit-20261013/README.md). The original submission artifacts below are retained unchanged. This is not acceptance or planet validation. See `submission-record.json` for verification and exact uploaded-file hashes.
- Zenodo evidence DOI: https://doi.org/10.5281/zenodo.23325261 (published 12 October UTC / 13 October IST). The GitHub integration is enabled. Original code is MIT; original text, figures and analysis products are CC BY 4.0; third-party terms remain in force (see `LICENSE` and `SOURCES.md`).
- The signal remains unvalidated. The modelled FPP is 0.06885, with unresolved host ambiguity and provisional novelty.

## Files and reproduction

`manuscript.json` is the text source; `build_manuscript.py` produces `rnaas.tex`, `rnaas.txt`, `rnaas-review.pdf` and `word-count.json`. The editable journal source uses AASTeX 7. The review PDF is separately typeset with ReportLab, not a compiled AASTeX proof. The AASTeX source was uploaded with the figure. `build_manuscript.py --submission-pdf` also produces `rnaas-author.pdf`, a separately typeset author-supplied PDF of the same text and figure, without review-status labels. This uses ReportLab, not a LaTeX compiler. The portal explicitly permits an author-supplied PDF when its converter is delayed. The three-page author PDF was visually checked locally and verified in the journal preview before submission. Earlier review PDFs and draft-labelled source metadata remain as preparation history.

`make_figure.py` renders one two-panel scientific figure from preserved numeric inputs. It does not refit the data. `figure_sources.json` records input paths and SHA-256 hashes. Run from a Python environment containing numpy/matplotlib; the manuscript builder requires ReportLab. Run both scripts from any directory (they resolve paths relative to this package).

`claim-sources.json` points reviewers to the saved evidence. `bulk-data-manifest.json` links and hashes the large original archives in the 10 October release. The repository source archive contains the tracked evidence and website; it does not include externally hosted bulk assets simply because they are linked.

## Preparation checklist (completed for initial submission)

1. Author metadata supplied: Independent researcher, New Delhi, India; kuberhob@gmail.com; ORCID 0009-0003-1379-7856.
2. Author reads and verifies the text, claims, figure, citations, attribution and AI disclosure. Resolve the THYME light-curve identity if possible; otherwise retain the explicit provisional-novelty language.
3. The working manuscript now cites the verified evidence DOI 10.5281/zenodo.23325261. This citation-only update postdates the frozen r2 evidence snapshot.
4. Inspect the journal-converted PDF or the permitted author-supplied PDF, then recount after any changes. Current draft: 1,203 words including 124-word abstract and one two-panel figure. Metadata additions may change the count.
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

The published Zenodo record metadata is preserved in `zenodo-record.json`. GitHub integration archived the repository source ZIP (118.2 MB), not the external bulk-data archives. Both the initial GitHub release and the DOI-backed r2 snapshot remain intact.
