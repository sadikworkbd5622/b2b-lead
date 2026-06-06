from datetime import datetime

from app.discovery.models import RawBusinessData


class TestRawBusinessData:
    def test_default_source(self):
        b = RawBusinessData(name="Test", source="serpapi")
        assert b.name == "Test"
        assert b.website is None
        assert b.phone is None
        assert b.rating is None

    def test_scraped_at_default(self):
        b = RawBusinessData(name="Test", source="serpapi")
        assert isinstance(b.scraped_at, datetime)

    def test_full_business(self):
        b = RawBusinessData(
            name="Joe's Pizza",
            address="123 Main St",
            phone="(555) 123-4567",
            website="joespizza.com",
            rating=4.5,
            reviews_count=120,
            category="Restaurant",
            latitude=32.7767,
            longitude=-96.7970,
            source="serpapi"
        )
        assert b.name == "Joe's Pizza"
        assert b.rating == 4.5
        assert b.latitude == 32.7767
