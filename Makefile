lint: clean
	- pip install ruff codespell -q
	- ruff check xorius/
	- codespell

format:
	- pip install ruff -q
	- ruff format xorius/

clean:
	- find . -iname "*__pycache__" | xargs rm -rf
	- find . -iname "*.pyc" | xargs rm -rf
	- rm cobertura.xml -f
	- rm testresult.xml -f
	- rm .coverage -f
	- rm .pytest_cache -rf
	- rm build/ -rf
	- rm dist -rf
	- rm *.egg-info -rf

test: clean
	- pip install -e .[test]
	- PYTHONPATH=. pytest tests/ -vvv --cov

lock-requirements:
	- pip install pip-tools -q
	- pip-compile -o requirements.txt

deps: lock-requirements
	- pip-sync

build: lint test
	- python -m build
