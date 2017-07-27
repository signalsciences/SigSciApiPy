lint: 
	flake8 SigSci.py --ignore=E501,E221,E272

reformat:
	autopep8 --in-place --aggressive --aggressive --ignore=E501 SigSci.py
