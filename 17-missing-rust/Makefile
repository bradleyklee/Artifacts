.PHONY: probe watch-go verify-transfer clean

probe:
	python3 run_probe.py

watch-go:
	python3 runtime_watch.py --label go-control --interval 0.02 -- go run samples/pi.go

verify-transfer:
	python3 verify_transfer.py

clean:
	rm -rf build/* reports/probe-*.md reports/resource-watch-*.md reports/resource-watch-*.csv
