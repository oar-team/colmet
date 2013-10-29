SHELL=/bin/bash
# these files should pass flake8
# exclude ./env/, which may contain virtualenv packages..;
WHITELIST_FILES:=$(shell find . -name '*.py' ! -path "*compat.py" ! -path "./env/*" \
           ! -path "./.tox/*")
IGNORE_LINT_ERRORS="W191,E128,E101,E121,E122,E123,E126,E127,E501"

# Dev
lint:
	@flake8 --ignore=${ignore_error} ${WHITELIST_FILES}

upgrade:
	@pip freeze --local | grep -v '^\-e' | cut -d = -f 1 | xargs pip install -U
freeze:
	@pip freeze --local

# Prod
deb:
	@python setup.py --command-packages=stdeb.command bdist_deb

# Common
doc:
	@cd docs; make html

clean:
	@git clean -Xfd


.PHONY: clean env doc
