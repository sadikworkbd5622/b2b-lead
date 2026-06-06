from app.qualification.models import URLType, WebsiteStatus


class TestWebsiteStatus:
    def test_live_dedicated(self):
        status = WebsiteStatus(
            is_live=True,
            final_url="https://example.com",
            status_code=200,
            url_type=URLType.DEDICATED_WEBSITE
        )
        assert status.is_live is True
        assert status.url_type == URLType.DEDICATED_WEBSITE
        assert status.status_code == 200

    def test_social_media(self):
        status = WebsiteStatus(
            is_live=False,
            final_url="https://facebook.com/biz",
            status_code=None,
            url_type=URLType.SOCIAL_MEDIA
        )
        assert status.is_live is False
        assert status.url_type == URLType.SOCIAL_MEDIA

    def test_no_url(self):
        status = WebsiteStatus(
            is_live=False,
            final_url=None,
            status_code=None,
            url_type=URLType.NO_URL
        )
        assert status.url_type == URLType.NO_URL

    def test_with_error(self):
        status = WebsiteStatus(
            is_live=False,
            final_url="https://example.com",
            status_code=None,
            url_type=URLType.DEDICATED_WEBSITE,
            error="Connection timeout"
        )
        assert status.error == "Connection timeout"
