# CRL Markdown Dataset

This repository is maintained as a structured research dataset for future website generation.

## Counts

- Research records: 86
- Bachelor records: 55
- Master records: 31
- Doctoral records: 0
- Members: 71
- Publications: 457
- Keywords: 307

## Canonical Markdown

- `dataset/research/records/<file_id>/`: per-thesis summary, detail, assets, and manifest
- `dataset/members/records/<member_id>.md`: member metadata and linked thesis records
- `dataset/publications/records/<publication_id>.md`: publication metadata and citation text
- `dataset/keywords/records/keyword-<hash>.md`: keyword metadata and related research links
- `dataset/quality.md`: gaps such as generic detail records and missing imagery

## Source Materials Kept In Repository

- `project/abst/`: summary markdown sources
- `project/detail/` and `project/detail_legacy/`: detailed markdown sources
- `proc/txt/`: full thesis markdown extracted from source documents
- `proc/img/`: thumbnails and selected research images
- `proc/img_all/`: extracted page images
- `pdfs/`: original or processed thesis PDFs when available

## Notes

- Students who continue from bachelor to master are represented by multiple thesis records linked from one member record.
- Thesis records are keyed by `file_id`, not by student name.
- The current dataset structure supports doctoral records, but none were detected in the present source files.
- This repository is now kept as a data-only snapshot; generation scripts are not included here.
