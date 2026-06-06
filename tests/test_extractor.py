import pytest

from app.analysis.models import ExtractedData, ExtractedLead


class TestExtractedLead:
    def test_qualified_status(self):
        lead = ExtractedLead(
            reasoning_log="No website found.",
            lead_status="Qualified - No Website",
            extracted_data=ExtractedData(
                business_name="Test Biz",
                decision_maker_name="John Doe",
                phone_number="(555) 123-4567",
                email_address="john@test.com",
                social_media_link="facebook.com/test"
            ),
            confidence_score=85
        )
        assert "Qualified" in lead.lead_status
        assert lead.extracted_data.business_name == "Test Biz"
        assert lead.extracted_data.phone_number == "(555) 123-4567"
        assert lead.confidence_score == 85

    def test_rejected_status(self):
        lead = ExtractedLead(
            reasoning_log="Has website.",
            lead_status="Rejected - Has Website",
            extracted_data=ExtractedData(
                business_name="Test Corp",
                decision_maker_name="Not Found",
                phone_number="Not Found",
                email_address="Not Found",
                social_media_link="Not Found"
            ),
            confidence_score=1
        )
        assert "Rejected" in lead.lead_status
        assert lead.confidence_score == 1

    def test_default_values(self):
        lead = ExtractedLead(
            reasoning_log="Test",
            lead_status="Qualified - No Website",
            extracted_data=ExtractedData(),
            confidence_score=50
        )
        assert lead.extracted_data.business_name == "Not Found"
        assert lead.extracted_data.phone_number == "Not Found"
        assert lead.extracted_data.email_address == "Not Found"

    def test_confidence_range(self):
        for score in [1, 50, 100]:
            lead = ExtractedLead(
                reasoning_log="Test",
                lead_status="Qualified - No Website",
                extracted_data=ExtractedData(business_name="Test"),
                confidence_score=score
            )
            assert 1 <= lead.confidence_score <= 100

    def test_invalid_confidence_below_range(self):
        with pytest.raises(Exception):
            ExtractedLead(
                reasoning_log="Test",
                lead_status="Qualified - No Website",
                extracted_data=ExtractedData(business_name="Test"),
                confidence_score=0
            )

    def test_invalid_status(self):
        with pytest.raises(Exception):
            ExtractedLead(
                reasoning_log="Test",
                lead_status="Invalid Status",
                extracted_data=ExtractedData(business_name="Test"),
                confidence_score=50
            )
