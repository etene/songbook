# My overkill CI-generated songbook

This repository contains the code used to generate my songbook in PDF format (using the Latex `songs` package) and put it somewhere handy on the Internet. A lot of things are done automatically, like the index generation and chord pattern insertion.

This way, I only have to put songs in the right directory, commit & push them and they're available from anywhere in a human-friendly format by scanning a (generated) QR code.

Using this to generate your own songbook should just be a matter of copying the repo, replacing the songs with your own and customizing the CI config.


## Automatic finger patterns

