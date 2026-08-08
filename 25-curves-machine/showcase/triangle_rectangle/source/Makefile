.PHONY: all verify figure levels verify-transforms analysis clean

all:
	python3 build.py

verify:
	cd payload && python3 verify_certificate.py

levels:
	python3 scripts/generate_quantized_levels.py

figure: levels
	python3 scripts/generate_figure.py


verify-transforms:
	python3 scripts/verify_hypergeometric_transform_chain.py

analysis: verify-transforms

clean:
	rm -f certificate_source.aux certificate_source.log certificate_source.out certificate_source.pdf
