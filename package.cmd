pipenv run pyroma -q -n 10 .

rmdir /s /q dist
rmdir /s /q build
rmdir /s /q pylint_utils.egg-info

pipenv run python -m build

pipenv run twine check dist/*
