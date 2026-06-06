from app.discovery.models import RawBusinessData
from app.pipeline.nodes import _cheap_classify, _dedup_key


class TestDedupKey:
    def test_with_phone(self):
        b = RawBusinessData(name="Test", phone="(214) 555-0132", source="serpapi")
        assert _dedup_key(b) == "(214) 555-0132"

    def test_with_website(self):
        b = RawBusinessData(name="Test", website="example.com", source="serpapi")
        assert _dedup_key(b) == "example.com"

    def test_with_website_trailing_slash(self):
        b = RawBusinessData(name="Test", website="Example.COM/", source="serpapi")
        assert _dedup_key(b) == "example.com"

    def test_with_name_only(self):
        b = RawBusinessData(name="Mike's BBQ Shack", source="serpapi")
        assert _dedup_key(b) == "mike's bbq shack"


class TestCheapClassify:
    def test_rejects_chain(self):
        b = RawBusinessData(name="McDonald's Corporate", source="serpapi")
        assert _cheap_classify(b) is False

    def test_rejects_llc(self):
        b = RawBusinessData(name="Acme Corp LLC", source="serpapi")
        assert _cheap_classify(b) is False

    def test_accepts_local(self):
        b = RawBusinessData(name="Mike's BBQ Shack", source="serpapi")
        assert _cheap_classify(b) is True

    def test_rejects_by_snippet(self):
        b = RawBusinessData(
            name="Some Restaurant",
            raw_snippet="A national chain with locations worldwide",
            source="serpapi"
        )
        assert _cheap_classify(b) is False
