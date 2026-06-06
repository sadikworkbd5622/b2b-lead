import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv

load_dotenv()

from app.config.loader import get_settings
from app.pipeline.graph import build_graph
from app.storage.database import DBLead, setup_database
from app.export.csv_export import export_to_csv
from app.export.json_export import export_to_json
from app.utils.logger import logger


def main():
    settings = get_settings("config/config.yaml")
    SessionLocal = setup_database()

    with SessionLocal() as db:
        count = db.query(DBLead).count()
        logger.info(f"Current DB has {count} lead(s)")
        db.query(DBLead).delete()
        db.commit()
        logger.info("Cleared all old leads (clean slate)")

    graph = build_graph(settings)

    initial_state = {
        "search_queries": [q.model_dump() for q in settings.search.queries],
        "max_results_per_query": settings.search.max_results_per_query,
        "raw_businesses": [],
        "qualified_raw_businesses": [],
        "extracted_leads": [],
        "qualified_leads": [],
        "rejected_leads": [],
        "enriched_leads": [],
        "errors": [],
        "current_step": "init",
        "stats": {},
    }

    logger.info("Re-running pipeline with cached SerpAPI data...")
    final_state = graph.invoke(initial_state)
    logger.info("Pipeline done.")

    all_extracted = final_state.get("extracted_leads", [])
    qualified = final_state.get("qualified_leads", [])
    enriched = final_state.get("enriched_leads", [])
    errors = final_state.get("errors", [])
    stats = final_state.get("stats", {})

    logger.info(
        f"Pipeline: {stats.get('discovered_count', 0)} discovered → "
        f"{stats.get('qualified_after_llm', 0)} qualified, "
        f"{stats.get('rejected_after_llm', 0)} rejected, "
        f"{stats.get('unprocessed_after_llm', 0)} unprocessed"
    )

    if all_extracted:
        with SessionLocal() as db:
            for lead in all_extracted:
                db.add(
                    DBLead(
                        business_name=lead.extracted_data.business_name,
                        decision_maker_name=lead.extracted_data.decision_maker_name,
                        phone_number=lead.extracted_data.phone_number,
                        email_address=lead.extracted_data.email_address,
                        social_media_link=lead.extracted_data.social_media_link,
                        lead_status=lead.lead_status,
                        confidence_score=lead.confidence_score,
                        reasoning_log=lead.reasoning_log,
                    )
                )
            db.commit()
        logger.info(f"Saved {len(all_extracted)} leads to DB")

    output_dir = settings.export.output_dir
    formats = settings.export.formats

    if "json" in formats and qualified:
        export_to_json(qualified, output_dir)
    if "csv" in formats and qualified:
        export_to_csv(qualified, output_dir)

    if enriched:
        import json as j

        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(output_dir, f"enriched_{ts}.json"), "w") as f:
            j.dump([r.model_dump() for r in enriched], f, indent=2)
        logger.info(f"Exported {len(enriched)} enriched leads")

    if errors:
        logger.warning(f"{len(errors)} error(s):")
        for e in errors:
            logger.warning(f"  {e}")

    logger.info(
        f"Done. {len(qualified)} qualified (of {stats.get('discovered_count', 0)}). "
        f"Dashboard → http://localhost:3000"
    )


if __name__ == "__main__":
    main()
