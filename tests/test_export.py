import json
import os
import tempfile

import pytest

from app.analysis.models import ExtractedData, ExtractedLead
from app.export.csv_export import export_to_csv
from app.export.json_export import export_to_json


@pytest.fixture
def leads():
    return [
        ExtractedLead(
            reasoning_log="No website",
            lead_status="Qualified - No Website",
            extracted_data=ExtractedData(
                business_name="Test Biz 1",
                decision_maker_name="John",
                phone_number="(555) 111-1111",
                email_address="john@test.com",
                social_media_link="fb.com/test1"
            ),
            confidence_score=80
        ),
        ExtractedLead(
            reasoning_log="Has website",
            lead_status="Rejected - Has Website",
            extracted_data=ExtractedData(
                business_name="Test Biz 2",
                decision_maker_name="Not Found",
                phone_number="Not Found",
                email_address="Not Found",
                social_media_link="Not Found"
            ),
            confidence_score=1
        )
    ]


class TestExport:
    def test_json_export(self, leads):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_to_json(leads, tmpdir)
            assert path is not None
            assert os.path.exists(path)
            with open(path) as f:
                data = json.load(f)
            assert len(data) == 2
            assert data[0]["extracted_data"]["business_name"] == "Test Biz 1"
            assert data[1]["lead_status"] == "Rejected - Has Website"

    def test_json_export_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_to_json([], tmpdir)
            assert path is None

    def test_csv_export(self, leads):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_to_csv(leads, tmpdir)
            assert path is not None
            assert os.path.exists(path)
            with open(path) as f:
                content = f.read()
            assert "business_name" in content
            assert "Test Biz 1" in content
            assert "Test Biz 2" in content

    def test_csv_export_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = export_to_csv([], tmpdir)
            assert path is None
