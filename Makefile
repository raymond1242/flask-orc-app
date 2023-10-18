compile-requirements:
	pip-compile requirements.in
install:
	pip install -r requirements.txt
run:
	flask --app main run --debug
