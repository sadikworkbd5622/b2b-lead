import csv
import os
from datetime import datetime

from app.analysis.models import ExtractedLead
from app.utils.logger import logger


def export_to_csv(leads: list[ExtractedLead], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"leads_{timestamp}.csv")

    if not leads:
        logger.info("No leads to export to CSV.")
        return None

    headers = [
        "business_name",
        "decision_maker_name",
        "phone_number",
        "email_address",
        "social_media_link",
        "confidence_score",
        "lead_status",
        "reasoning_log"
    ]

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for lead in leads:
            row = {
                "business_name": lead.extracted_data.business_name,
                "decision_maker_name": lead.extracted_data.decision_maker_name,
                "phone_number": lead.extracted_data.phone_number,
                "email_address": lead.extracted_data.email_address,
                "social_media_link": lead.extracted_data.social_media_link,
                "confidence_score": lead.confidence_score,
                "lead_status": lead.lead_status,
                "reasoning_log": lead.reasoning_log
            }
            writer.writerow(row)

    logger.info(f"Exported {len(leads)} leads to CSV: {filepath}")
    return filepath
