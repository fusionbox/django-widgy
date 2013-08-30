JS_FILES?=$(shell find ./js_tests/tests -type f -name '*.js')
MOCHA_REPORTER=nyan

test: test-py test-js

coverage: coverage-py coverage-js

browser: browser-py browser-js

test-py:
	cd tests && $(COVERAGE_COMMAND) ./runtests.py --settings=test_multidb --verbosity=2 $(TESTS)

coverage-py:
	+make test-py COVERAGE_COMMAND='coverage run --source=widgy'
	cd tests && coverage html --omit='../widgy/migrations/*,../widgy/contrib/*/migrations/*'

browser-py: coverage-py
	sensible-browser tests/coverage_html/index.html

js_tests/node_modules: js_tests/package.json
	cd js_tests && npm install .

test-js: js_tests/node_modules
	@./js_tests/node_modules/mocha/bin/mocha \
		-s 5 \
		--reporter $(MOCHA_REPORTER) \
		$(JS_FILES)

js_tests/coverage_js: js_tests/node_modules $(shell find widgy/static/widgy/js -type f -iregex '.*\.js')
	-rm -r $@
	./js_tests/node_modules/visionmedia-jscoverage/jscoverage widgy/static/widgy/js/ $@ \
		--no-instrument=lib

# The sed is to remove an artifact from the make call.
coverage-js: js_tests/coverage_js
	COVERAGE=1 $(MAKE) test-js MOCHA_REPORTER=html-cov | sed '1d' > ./js_tests/coverage.html

browser-js: coverage-js
	sensible-browser js_tests/coverage.html

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


.PHONY: test coverage browser test-py coverage-py browser-py test-js coverage-js browser-js docs
