all: build/songbook.pdf

view: build/songbook.pdf
	xdg-open $^

build/songs/*.tex: songs/*.tex
	mkdir -vp build/songs
	sh -exc 'for i in $^; do python3.12 -m songbook_tools insertchords $$i > build/$$i; done'

build/songlist.tex: build/songs/*.tex songbook_tools/*.py
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

build/songbook.pdf: build/chords.tex build/songlist.tex build/buildinfo.tex build/songs/*.tex build/songbook.tex
	cd build && pdflatex songbook.tex
	texlua scripts/songidx.lua build/songsindex.sxd build/songsindex.sbx
	cd build && pdflatex songbook.tex

clean:
	rm -rf build
