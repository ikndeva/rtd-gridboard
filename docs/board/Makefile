# makefile

.SUFFIXES: .py .pdf .png .exp .test 

.py.exp:
	python3 $*.py $*.pdf 

##
DO_COLORIZE= | ../colorize_trace.sh 
DO_OPEN= && open out.pdf
UBCMD=unbuffer
OPTB=
TESTDIR=./ctest
OFILE=out.pdf

.py.test: 
	$(UBCMD) python3 $*.py $(OPTB) $(DO_COLORIZE) && mv out.pdf $(OFILE) && open $(OFILE)


test:
	make OPTB='-b -m 0.2' OFILE='out13.pdf' ctest/ctest13packer.test
	make OPTB='-b' OFILE='out14.pdf' ctest/ctest14packer.test

test.all:
	make ctest/ctest7cboard.test
	make ctest/ctest8cbd.test
	make ctest/ctest9cbdlines.test
	make ctest/ctest10randwalk.test
	make ctest/ctest11cbd.test 
	make ctest/ctest12anchor.test
	make ctest/ctest13packer.test
	make ctest/ctest13packer.test
	make ctest/ctest14packer.test
	make ctest/ctest14packer.test

# test.list:
# 	history | grep ctest | grep 'make' | cut -b8- | grep '^make' | grep -v 'cb\|-n' | sort -u

##
color_chart: 
	python3 color_chart.py

##
TARGET=test1.exp 

all: $(TARGET)

clean:
	rm -f  *~ *.pdf *.png $(TARGET)

cleanall:
	make clean
	rm -fr __pycache__ 


## EOF

