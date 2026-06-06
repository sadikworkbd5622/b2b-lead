import json
import os
from datetime import datetime

from app.analysis.models import ExtractedLead
from app.utils.logger import logger


def export_to_json(leads: list[ExtractedLead], output_dir: str):
    os.makedirs(output_dir, exist_ok=True)

    if not leads:
        logger.info("No leads to export to JSON.")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(output_dir, f"leads_{timestamp}.json")

    data = [lead.model_dump() for lead in leads]

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    logger.info(f"Exported {len(leads)} leads to JSON: {filepath}")
    return filepath
