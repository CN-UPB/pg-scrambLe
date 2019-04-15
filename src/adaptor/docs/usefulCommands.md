+ To generate wheels

python3 setup.py sdist bdist_wheel

+ To upload to pypi

twine upload dist/*

+ add pypi details

nano ~/.pypirc

[distutils]
index-servers =
    pypi

[pypi]
repository: https://test.pypi.org/legacy/
username: test-pgscramble
password: 

+ To clean build files

python3 setup.py clean --all

+ To build sphinx document

sphinx-build -b html . ./doc
