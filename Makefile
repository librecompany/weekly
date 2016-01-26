# Public domain 2013, Simone Basso <bassosimone@gmail.com>
.PHONY: clean
clean:
	find . -type f -name \*~ -exec rm {} \;
	find . -type f -name \*.pyc -exec rm {} \;
