.PHONY: all verify figure clean

all:
	python3 build.py

verify:
	cd payload && python3 verify_certificate.py

figure:
	python3 scripts/generate_figure.py

clean:
	rm -f certificate_source.aux certificate_source.log certificate_source.pdf
