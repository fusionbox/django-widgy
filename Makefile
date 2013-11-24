JS_FILES?=`find ./js_tests/tests -type f -name '*.js'`

test: test-py test-js

test-py:
	cd tests && $(COVERAGE_COMMAND) ./runtests.py --settings=test_multidb --verbosity=2 $(TESTS)

coverage:
	+make test-py COVERAGE_COMMAND='coverage run --source=widgy'
	cd tests && coverage html --omit='../widgy/migrations/*,../widgy/contrib/*/migrations/*'

browser: coverage
	sensible-browser tests/coverage_html/index.html

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
