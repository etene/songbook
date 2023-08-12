all: build/songbook.pdf

view: all
	xdg-open build/songbook.pdf

build:
	mkdir -vp build

build/songs: songs/*.tex build
	ln -vfs ../songs $@

build/songlist.tex: build/songs scripts/makesonglist.py
	python3 scripts/makesonglist.py songs > $@

build/songbook.tex: build template.tex newline-fix.tex scripts/apply_newline_fix.sh
	cp -v template.tex $@
	scripts/apply_newline_fix.sh $@

build/chords.tex: build scripts/chords.py chords/*.ini
	python3 scripts/chords.py chords/ukulele.ini > $@

build/songbook.pdf: build/songlist.tex build/songbook.tex build/chords.tex
	cd build && pdflatex songbook.tex
	texlua scripts/songidx.lua build/songsindex.sxd build/songsindex.sbx
	cd build && pdflatex songbook.tex

clean:
	rm -rf build
