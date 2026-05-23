# crl_web_2025 dataset workflow
#
# Typical annual onboarding (one thesis):
#   make convert PDF=pdfs/2026_M_foo.pdf
#   make strip-toc            # idempotent; safe to run any time
#   make scaffold FILE_ID=2026_M_foo TITLE='...' TITLE_EN='...' \
#                 STUDENT_ID=25KMH01 MEMBER_NAME='山田 太郎'
#   make derive               # regenerate data/*.json and dataset/quality.md
#
# Quality maintenance:
#   make derive               # refresh derived artifacts from dataset/

PY := python3
SCRIPTS := scripts

.PHONY: help convert strip-toc scaffold derive check

help:
	@echo "Targets:"
	@echo "  convert PDF=<path>                          markitdown → proc/txt/<id>.md"
	@echo "  strip-toc                                   strip TOC from every proc/txt/*.md"
	@echo "  scaffold FILE_ID=... TITLE=... TITLE_EN=... STUDENT_ID=... MEMBER_NAME=..."
	@echo "                                              create dataset/research/records/<file_id>/"
	@echo "  derive                                      rebuild data/*.json and dataset/quality.md"
	@echo "  check                                       dry-run: ensure derive is up-to-date"

convert:
	@test -n "$(PDF)" || (echo "PDF= is required"; exit 2)
	$(PY) $(SCRIPTS)/convert_thesis.py $(PDF)

strip-toc:
	$(PY) $(SCRIPTS)/strip_toc.py proc/txt/*.md

scaffold:
	@test -n "$(FILE_ID)" || (echo "FILE_ID= is required"; exit 2)
	@test -n "$(TITLE)" || (echo "TITLE= is required"; exit 2)
	@test -n "$(STUDENT_ID)" || (echo "STUDENT_ID= is required"; exit 2)
	@test -n "$(MEMBER_NAME)" || (echo "MEMBER_NAME= is required"; exit 2)
	$(PY) $(SCRIPTS)/scaffold_record.py \
		--file-id '$(FILE_ID)' \
		--title '$(TITLE)' \
		--title-en '$(TITLE_EN)' \
		--student-id '$(STUDENT_ID)' \
		--member-name '$(MEMBER_NAME)'

derive:
	$(PY) $(SCRIPTS)/build_derived.py
	$(PY) $(SCRIPTS)/build_web_views.py

check:
	@tmp=$$(mktemp -d); \
	cp data/thesis.json $$tmp/; cp data/members.json $$tmp/; cp dataset/quality.md $$tmp/; \
	cp data/cards.json $$tmp/; cp data/facets.json $$tmp/; \
	$(PY) $(SCRIPTS)/build_derived.py >/dev/null; \
	$(PY) $(SCRIPTS)/build_web_views.py >/dev/null; \
	diff -q $$tmp/thesis.json data/thesis.json && \
	diff -q $$tmp/members.json data/members.json && \
	diff -q $$tmp/quality.md dataset/quality.md && \
	diff -q $$tmp/cards.json data/cards.json && \
	diff -q $$tmp/facets.json data/facets.json; \
	status=$$?; \
	cp $$tmp/thesis.json data/; cp $$tmp/members.json data/; cp $$tmp/quality.md dataset/; \
	cp $$tmp/cards.json data/; cp $$tmp/facets.json data/; \
	rm -rf $$tmp; \
	if [ $$status -ne 0 ]; then \
	  echo "derived artifacts are stale — run 'make derive'"; exit 1; \
	fi
