install:
	pip install -r requirements.txt
	# curl -L https://git.io/misspell | bash
lint: 
	pylint SigSci.py
	flake8 SigSci.py test_SigSci.py --ignore=E501

reformat:
	autopep8 --in-place --aggressive --aggressive --ignore=E501 SigSci.py

misspell:
	./bin/misspell SigSci.py

test:
	nosetests --with-coverage --cover-package=SigSciApiPy

clean:
	rm -f *.pyc
	rm -rf cover
	rm -rf bin
