CXX ?= g++
CXXFLAGS ?= -O3 -std=c++20 -Wall -Wextra -Wpedantic

all: disk_polyomino

disk_polyomino: disk_polyomino.cpp
	$(CXX) $(CXXFLAGS) -o $@ $<

clean:
	rm -f disk_polyomino *.csv
