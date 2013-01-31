test:
	cd tests && $(COVERAGE_COMMAND) ./runtests.py --settings=test_multidb --verbosity=2 $(TESTS)

coverage:
	+make test COVERAGE_COMMAND='coverage run --source=widgy'
	cd tests && coverage html --omit='../widgy/migrations/*,../widgy/contrib/*/migrations/*'

browser: coverage
	sensible-browser tests/coverage_html/index.html

.PHONY: test coverage browser
