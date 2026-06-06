from app.enrichment.models import EnrichmentResult


class TestEnrichmentResult:
    def test_default_values(self):
        result = EnrichmentResult(business_name="Test Biz")
        assert result.business_name == "Test Biz"
        assert result.domain is None
        assert result.email_address is None
        assert result.confidence == 0
        assert result.source == "unknown"

    def test_full_result(self):
        result = EnrichmentResult(
            business_name="Test Biz",
            domain="testbiz.com",
            decision_maker_name="John Doe",
            email_address="john@testbiz.com",
            phone_number="(555) 123-4567",
            confidence=80,
            source="hunter"
        )
        assert result.email_address == "john@testbiz.com"
        assert result.confidence == 80
        assert result.source == "hunter"

    def test_error_result(self):
        result = EnrichmentResult(
            business_name="Test Biz",
            source="hunter",
            error="API key not configured"
        )
        assert result.error == "API key not configured"
        assert result.confidence == 0

    def test_confidence_range(self):
        for score in [0, 50, 100]:
            result = EnrichmentResult(
                business_name="Test",
                confidence=score
            )
            assert 0 <= result.confidence <= 100
