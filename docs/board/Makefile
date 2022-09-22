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

testall:
	make $(TESTDIR)/ctest0.test
	make $(TESTDIR)/ctest1.test 
	make $(TESTDIR)/ctest2.test
	make $(TESTDIR)/ctest3.test
	make $(TESTDIR)/ctest4.test
	make $(TESTDIR)/ctest5colorchart.test
	make $(TESTDIR)/ctest6colorchart.test
	make $(TESTDIR)/ctest7cboard.test
	make $(TESTDIR)/ctest8cbd.test
	make $(TESTDIR)/ctest9cbdlines.test
	make $(TESTDIR)/ctest10randwalk.test
	make $(TESTDIR)/ctest11randwalk.test

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

