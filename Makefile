SONGBOOK=perso
SONGS_BUILD_DIR=build/$(SONGBOOK)/songs
SONGS=$(wildcard songbooks/$(SONGBOOK)/*.tex)
BUILT_SONGS=$(patsubst songbooks/$(SONGBOOK)/%.tex,$(SONGS_BUILD_DIR)/%.tex,$(SONGS))
INSTRUMENT=ukulele
CHORDS_PER_LINE=8

all: build/$(SONGBOOK).pdf

view: build/$(SONGBOOK).pdf
	xdg-open ./$^

$(SONGS_BUILD_DIR):
	mkdir -vp $(SONGS_BUILD_DIR)

$(BUILT_SONGS): $(SONGS_BUILD_DIR)/%.tex: songbooks/$(SONGBOOK)/%.tex | $(SONGS_BUILD_DIR)
ifeq ("$(INSTRUMENT)","")
	cp -v $< $@
else
	python3.13 -m songbook_tools insertchords --chords-per-line $(CHORDS_PER_LINE) $< > $@
endif

build/$(SONGBOOK)/songlist.tex: $(BUILT_SONGS) songbook_tools/*.py
	cd build/$(SONGBOOK) && PYTHONPATH=../.. python3.13 -m songbook_tools makesonglist songs > ../../$@

build/$(SONGBOOK)/buildinfo.tex: songbook_tools/*.py
	mkdir -vp build/$(SONGBOOK)
	python3.13 -m songbook_tools makebuildinfo > $@

build/$(SONGBOOK)/$(SONGBOOK).tex: template.tex newline-fix.tex scripts/apply_newline_fix.sh
	cp -v template.tex $@
	scripts/apply_newline_fix.sh $@

build/$(SONGBOOK)/chords.tex: songbook_tools/*.py chords/*.ini
	mkdir -vp build/$(SONGBOOK)
ifneq ($(INSTRUMENT),)
	python3.13 -m songbook_tools makechords chords/$(INSTRUMENT).ini > $@
endif

build/$(SONGBOOK).pdf: build/$(SONGBOOK)/chords.tex build/$(SONGBOOK)/songlist.tex build/$(SONGBOOK)/buildinfo.tex $(BUILT_SONGS) build/$(SONGBOOK)/$(SONGBOOK).tex
	cd build/$(SONGBOOK) && pdflatex $(SONGBOOK).tex
	texlua scripts/songidx.lua build/$(SONGBOOK)/songsindex.sxd build/$(SONGBOOK)/songsindex.sbx
	cd build/$(SONGBOOK) && pdflatex $(SONGBOOK).tex
	cp build/$(SONGBOOK)/$(SONGBOOK).pdf build/$(SONGBOOK).pdf

clean:
	rm -rf build/

