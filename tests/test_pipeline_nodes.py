from app.discovery.models import RawBusinessData
from app.pipeline.nodes import _cheap_classify, _dedup_key, _fuzzy_dedup


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


class TestFuzzyDedup:
    def test_near_duplicate_names(self):
        b1 = RawBusinessData(name="Mike's BBQ Shack", phone="(214) 555-0132", source="serpapi")
        b2 = RawBusinessData(name="Mikes BBQ Shack", phone="(214) 555-0132", source="serpapi")
        b3 = RawBusinessData(name="Totally Different", phone="(512) 555-9999", source="serpapi")
        result = _fuzzy_dedup([b1, b2, b3], threshold=0.8)
        assert len(result) == 2
        assert result[0].name == "Mike's BBQ Shack"
        assert result[1].name == "Totally Different"

    def test_threshold_zero_disabled(self):
        b1 = RawBusinessData(name="Mike's BBQ Shack", source="serpapi")
        b2 = RawBusinessData(name="Mike's BBQ Shack!!", source="serpapi")
        result = _fuzzy_dedup([b1, b2], threshold=0.0)
        assert len(result) == 2

    def test_keeps_more_informative(self):
        no_info = RawBusinessData(name="Mike's BBQ Shack", source="serpapi")
        has_info = RawBusinessData(name="Mikes BBQ Shack", phone="(214) 555-0132", source="serpapi")
        result = _fuzzy_dedup([no_info, has_info], threshold=0.8)
        assert len(result) == 1
        assert result[0].phone == "(214) 555-0132"

    def test_empty_list(self):
        assert _fuzzy_dedup([], threshold=0.85) == []

    def test_single_business(self):
        b = RawBusinessData(name="Only One", source="serpapi")
        assert _fuzzy_dedup([b], threshold=0.85) == [b]
