DJANGO_SETTINGS_MODULE?=tests.settings_contrib

test: test-py test-js

test-py:
	DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE) pytest $(PYTEST_OPTIONS)

coverage:
	+make test-py PYTEST_OPTIONS='--cov widgy'
	coverage html --omit='widgy/*migrations/*,widgy/contrib/*/*migrations/*,'

browser: coverage
	sensible-browser ./htmlcov/index.html

js_tests/node_modules: js_tests/package.json
	cd js_tests && npm install --no-package-lock .

test-js: js_tests/node_modules
	node -v
	cd js_tests && npm test tests

widgy/locale/en/LC_MESSAGES/django.po: $(shell find . -type f -iregex '.*\.\(html\|py\|md\)$$')

	cd widgy && django-admin.py makemessages -l en

widgy/locale/xx_pseudo/LC_MESSAGES/django.po: widgy/locale/en/LC_MESSAGES/django.po
	-rm -r "`dirname $@`"
	potpie $< $@

widgy/locale/xx_pseudo/LC_MESSAGES/django.mo: widgy/locale/xx_pseudo/LC_MESSAGES/django.po
	cd widgy && django-admin.py compilemessages

t10n: widgy/locale/xx_pseudo/LC_MESSAGES/django.mo

docs:
	cd docs && $(MAKE) html

# Stylesheets. Widgy ships compiled CSS (committed to the repo) so that
# projects using it need no Sass compiler. See bin/build-css.mjs for the list
# of entry points. Run `make css` after editing SCSS, and commit the result.
node_modules: package.json
	npm install --no-package-lock
	touch $@

css: node_modules
	node bin/build-css.mjs

# Fails if the committed CSS is out of date with the SCSS sources.
css-check: css
	git diff --exit-code -- '*.css'
	@test -z "$$(git ls-files --others --exclude-standard -- '*.css')" || \
		{ echo "Untracked compiled CSS; run make css and commit."; exit 1; }


.PHONY: test coverage browser test-py test-js docs css css-check
