# makefile

.SUFFIXES: .py .pdf .png .exp .test 

.py.exp:
	python3 $*.py $*.pdf 

##
DO_COLORIZE= | ../colorize_trace.sh 
DO_OPEN= && open out.pdf
UBCMD=unbuffer
OPT_BD=
TESTDIR=./ctest

.py.test: 
	$(UBCMD) python3 $*.py $(OPT_BD) $(DO_COLORIZE) $(DO_OPEN)

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

# クラス図とパッケージ図
## required: [pip] pylint (pyreverse), [brew] graphviz (dot)
## クラス図とパッケージ図を生成する
class:
	pyreverse -k -o pdf board

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

