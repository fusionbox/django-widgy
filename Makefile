JS_FILES?=`find ./js_tests/tests -type f -name '*.js'`

test: test-py test-js

test-py:
	cd tests && $(COVERAGE_COMMAND) ./runtests.py --settings=test_multidb --verbosity=2 $(TESTS)

coverage:
	+make test COVERAGE_COMMAND='coverage run --source=widgy'
	cd tests && coverage html --omit='../widgy/migrations/*,../widgy/contrib/*/migrations/*'

browser: coverage
	sensible-browser tests/coverage_html/index.html

js_tests/node_modules: js_tests/package.json
	cd js_tests && npm install .

test-js: js_tests/node_modules
	./js_tests/node_modules/mocha/bin/mocha \
		--reporter spec \
		-s 5 \
		--globals _,Backbone \
		$(JS_FILES)

.PHONY: test coverage browser test-py test-js
