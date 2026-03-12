
GXX49_VERSION := $(shell g++-4.9 --version 2>/dev/null)

ifdef GXX49_VERSION
	CXX_COMMAND := g++-4.9
else
	CXX_COMMAND := g++
endif

CXX = ${CXX_COMMAND} -std=c++17 -Wall

run_test: maxweight_test
	./maxweight_test

headers: rubrictest.hh maxweight.hh

maxweight_test: headers maxweight_test.cc
	${CXX} maxweight_test.cc -o maxweight_test

maxweight_scatterplot: maxweight.hh maxweight_scatterplot.cc timer.hh
	${CXX} maxweight_scatterplot.cc -o maxweight_scatterplot

# Generate enhanced CSV files with solution metrics
benchmark: maxweight_scatterplot
	./maxweight_scatterplot

# Generate all visualizations (static + interactive)
visualize: benchmark
	python3 visualize.py --all

# Quick visualization (static PNG plots only)
plots: benchmark
	python3 visualize.py --static

# Interactive dashboard only
interactive: benchmark
	python3 visualize.py --interactive
	@echo ""
	@echo "Open plots/interactive_dashboard.html in your browser"

# Complete workflow: test, benchmark, and visualize
all: run_test benchmark visualize

# Clean including plots and CSV files
clean_all: clean
	rm -rf plots/ *_detailed.csv comparison.csv
	rm -f maxweight_scatterplot

clean:
	rm -f maxweight_test
