from django.test import TestCase


class CurlieRegexTests(TestCase):

    def test_no_curlie_regex_empty(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'') is not None

    def test_no_curlie_regex_matches_non_curlies_single_char(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'a') is not None

    def test_no_curlie_regex_matches_non_curlies_many_chars(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'This has no curlies') is not None

    def test_no_curlie_regex_doesnt_match_single_curlies(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'{') is None
        assert no_curlies_regex.match(u'}') is None
        assert no_curlies_regex.match(u'{a}') is None
        assert no_curlies_regex.match(u'{a}') is None

    def test_no_curlie_regex_doesnt_match_just_curlies(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'}}') is None
        assert no_curlies_regex.match(u'{{') is None

    def test_no_curlie_regex_doesnt_match_with_characters_curlies(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'{{a}}') is None
        assert no_curlies_regex.match(u'{{ This has curlies }}') is None
