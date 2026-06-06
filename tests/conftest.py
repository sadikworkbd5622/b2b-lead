import pytest

from app.analysis.models import ExtractedData, ExtractedLead
from app.discovery.models import RawBusinessData
from app.qualification.url_classifier import URLClassifier
from app.qualification.website_checker import WebsiteChecker


@pytest.fixture
def classifier():
    return URLClassifier(non_website_domains=[
        "facebook.com", "instagram.com", "yelp.com",
        "yellowpages.com", "linktr.ee", "twitter.com",
        "tiktok.com"
    ])


@pytest.fixture
def checker(classifier):
    return WebsiteChecker(classifier=classifier, timeout=5)


@pytest.fixture
def business_no_website():
    return RawBusinessData(
        name="Mike's BBQ Shack",
        address="123 Main St, Dallas, TX",
        phone="(214) 555-0132",
        website="facebook.com/mikesbbq",
        rating=4.5,
        category="Restaurant",
        source="serpapi"
    )


@pytest.fixture
def business_with_website():
    return RawBusinessData(
        name="Austin Plumbing Pros",
        address="456 Oak Ave, Austin, TX",
        phone="(512) 555-0199",
        website="austinplumbingpros.com",
        rating=4.2,
        category="Plumber",
        source="serpapi"
    )


@pytest.fixture
def business_no_url():
    return RawBusinessData(
        name="Corner Grocery",
        address="789 Elm St",
        phone="(972) 555-0111",
        website=None,
        category="Grocery",
        source="serpapi"
    )


@pytest.fixture
def qualified_lead():
    return ExtractedLead(
        reasoning_log="No dedicated website, only Facebook page.",
        lead_status="Qualified - No Website",
        extracted_data=ExtractedData(
            business_name="Mike's BBQ Shack",
            decision_maker_name="Mike Johnson",
            phone_number="(214) 555-0132",
            email_address="mike@bbqshack.com",
            social_media_link="facebook.com/mikesbbq"
        ),
        confidence_score=75
    )


@pytest.fixture
def rejected_lead():
    return ExtractedLead(
        reasoning_log="Has dedicated website.",
        lead_status="Rejected - Has Website",
        extracted_data=ExtractedData(
            business_name="Austin Plumbing Pros",
            decision_maker_name="Not Found",
            phone_number="Not Found",
            email_address="Not Found",
            social_media_link="Not Found"
        ),
        confidence_score=1
    )
