from django.test import TestCase

class CurlieRegexTests(TestCase):

    def test_curlie_regex_matches_non_curlies(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'') is not None
        assert no_curlies_regex.match(u'a') is not None
        assert no_curlies_regex.match(u'This has no curlies') is not None


    def test_curlie_regex_doesnt_match_curlies(self):
        from .models import no_curlies_regex
        assert no_curlies_regex.match(u'{') is None
        assert no_curlies_regex.match(u'}') is None
        assert no_curlies_regex.match(u'{a}') is None
        assert no_curlies_regex.match(u'{a}') is None
        assert no_curlies_regex.match(u'}}') is None
        assert no_curlies_regex.match(u'{{') is None
        assert no_curlies_regex.match(u'{{a}}') is None
        assert no_curlies_regex.match(u'{{a}}') is None
        assert no_curlies_regex.match(u'{{ This has curlies }}') is None
