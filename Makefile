lint: 
	pylint SigSci.py
	flake8 SigSci.py --ignore=E501

reformat:
	autopep8 --in-place --aggressive --aggressive --ignore=E501 SigSci.py
