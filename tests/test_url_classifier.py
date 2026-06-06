"""Renamed from test_qualification.py for clarity."""
import pytest

from app.qualification.models import URLType
from app.qualification.url_classifier import URLClassifier


@pytest.fixture
def classifier():
    return URLClassifier(non_website_domains=[
        "facebook.com", "instagram.com", "yelp.com",
        "linktr.ee", "twitter.com", "x.com", "tiktok.com",
        "yellowpages.com", "tripadvisor.com", "bbb.org"
    ])


class TestURLClassifier:
    def test_no_url(self, classifier):
        assert classifier.classify(None) == URLType.NO_URL
        assert classifier.classify("") == URLType.NO_URL
        assert classifier.classify("   ") == URLType.NO_URL

    def test_social_media(self, classifier):
        assert classifier.classify("https://facebook.com/mybusiness") == URLType.SOCIAL_MEDIA
        assert classifier.classify("http://www.instagram.com/mybusiness") == URLType.SOCIAL_MEDIA
        assert classifier.classify("https://twitter.com/mybusiness") == URLType.SOCIAL_MEDIA
        assert classifier.classify("https://www.x.com/mybusiness") == URLType.SOCIAL_MEDIA

    def test_directory(self, classifier):
        assert classifier.classify("https://yelp.com/biz/mybusiness") == URLType.DIRECTORY_LISTING
        assert classifier.classify("https://yellowpages.com/biz") == URLType.DIRECTORY_LISTING
        assert classifier.classify("https://www.tripadvisor.com/restaurant") == URLType.DIRECTORY_LISTING

    def test_link_in_bio(self, classifier):
        assert classifier.classify("https://linktr.ee/mybusiness") == URLType.LINK_IN_BIO

    def test_dedicated_website(self, classifier):
        assert classifier.classify("https://www.joesplumbing.com") == URLType.DEDICATED_WEBSITE
        assert classifier.classify("http://austinpipes.net/about") == URLType.DEDICATED_WEBSITE
        assert classifier.classify("mybusiness.org") == URLType.DEDICATED_WEBSITE
        assert classifier.classify("https://example.com") == URLType.DEDICATED_WEBSITE

    def test_subdomain_handling(self, classifier):
        assert classifier.classify("https://shop.example.com") == URLType.DEDICATED_WEBSITE
        assert classifier.classify("https://www.facebook.com") == URLType.SOCIAL_MEDIA

    def test_case_insensitive(self, classifier):
        assert classifier.classify("https://FACEBOOK.com/mybusiness") == URLType.SOCIAL_MEDIA
        assert classifier.classify("https://YELP.com/biz") == URLType.DIRECTORY_LISTING
