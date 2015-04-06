JS_FILES?=`find ./js_tests/tests -type f -name '*.js'`
DJANGO_SETTINGS_MODULE?=tests.settings_contrib

test: test-py test-js

test-py:
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) py.test $(PYTEST_OPTIONS)

coverage:
	+make test-py PYTEST_OPTIONS='--cov widgy'
	coverage html --omit='widgy/*migrations/*,widgy/contrib/*/*migrations/*,'

browser: coverage
	sensible-browser ./htmlcov/index.html

js_tests/node_modules: js_tests/package.json
	cd js_tests && npm install .

test-js: js_tests/node_modules
	./js_tests/node_modules/mocha/bin/mocha \
		-s 5 \
		--reporter spec \
		$(JS_FILES)

widgy/locale/en/LC_MESSAGES/django.po: $(shell find . -type f -iregex '.*\.\(html\|py\|md\)$$' | grep -v .tox)

	cd widgy && django-admin.py makemessages -l en

widgy/locale/xx_pseudo/LC_MESSAGES/django.po: widgy/locale/en/LC_MESSAGES/django.po
	-rm -r "`dirname $@`"
	potpie $< $@

widgy/locale/xx_pseudo/LC_MESSAGES/django.mo: widgy/locale/xx_pseudo/LC_MESSAGES/django.po
	cd widgy && django-admin.py compilemessages

t10n: widgy/locale/xx_pseudo/LC_MESSAGES/django.mo

docs:
	cd docs && $(MAKE) html


.PHONY: test coverage browser test-py test-js docs
