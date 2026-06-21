CXX ?= g++
CXXFLAGS ?= -O3 -std=c++20 -Wall -Wextra -Wpedantic

all: ellipse_polyomino

ellipse_polyomino: ellipse_polyomino.cpp
	$(CXX) $(CXXFLAGS) $< -o $@

clean:
	rm -f ellipse_polyomino
