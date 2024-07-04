SONGS_BUILD_DIR=build/songs
SONGS=$(wildcard songs/*.tex)
BUILT_SONGS=$(patsubst songs/%.tex,$(SONGS_BUILD_DIR)/%.tex,$(SONGS))

all: build/songbook.pdf

view: build/songbook.pdf
	xdg-open $^

$(SONGS_BUILD_DIR):
	mkdir -vp $(SONGS_BUILD_DIR)

$(BUILT_SONGS): $(SONGS_BUILD_DIR)/%.tex: songs/%.tex | $(SONGS_BUILD_DIR)
	python3.12 -m songbook_tools insertchords $< > $@

build/songlist.tex: $(BUILT_SONGS) songbook_tools/*.py
	python3.12 -m songbook_tools makesonglist songs > $@

build/buildinfo.tex: songbook_tools/*.py
	mkdir -vp build
	python3.12 -m songbook_tools makebuildinfo > $@

build/songbook.tex: template.tex newline-fix.tex scripts/apply_newline_fix.sh
	cp -v template.tex $@
	scripts/apply_newline_fix.sh $@

build/chords.tex: songbook_tools/*.py chords/*.ini
	mkdir -vp build
	python3.12 -m songbook_tools makechords chords/ukulele.ini > $@

build/songbook.pdf: build/chords.tex build/songlist.tex build/buildinfo.tex $(BUILT_SONGS) build/songbook.tex
	cd build && pdflatex songbook.tex
	texlua scripts/songidx.lua build/songsindex.sxd build/songsindex.sbx
	cd build && pdflatex songbook.tex

clean:
	rm -rf build

lint:
	chktex $(SONGS)
