
import typer
from dotenv import load_dotenv

from app.config.loader import get_settings
from app.export.csv_export import export_to_csv
from app.export.json_export import export_to_json
from app.pipeline.graph import build_graph
from app.storage.database import DBLead, setup_database
from app.utils.logger import logger

load_dotenv()

app = typer.Typer(help="B2B Lead Generation AI Agent CLI")


@app.command()
def run(config_path: str = "config/config.yaml"):
    logger.info(f"Loading configuration from {config_path}")
    settings = get_settings(config_path)

    SessionLocal = setup_database()

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
        "stats": {}
    }

    logger.info("Starting pipeline execution...")
    final_state = graph.invoke(initial_state)
    logger.info("Pipeline execution completed.")

    stats = final_state.get("stats", {})
    logger.info(f"Discovered: {stats.get('discovered_count', '?')} businesses")
    logger.info(f"After dedup: {stats.get('after_dedup', '?')}")
    logger.info(f"After qualification: {stats.get('qualified_at_qualify', '?')} kept, {stats.get('rejected_at_qualify', '?')} rejected")
    logger.info(f"After LLM: {stats.get('qualified_after_llm', '?')} qualified, {stats.get('rejected_after_llm', '?')} rejected, {stats.get('unprocessed_after_llm', '?')} unprocessed")

    all_extracted = final_state.get("extracted_leads", [])
    qualified = final_state.get("qualified_leads", [])
    enriched = final_state.get("enriched_leads", [])
    errors = final_state.get("errors", [])

    if all_extracted:
        with SessionLocal() as db:
            for lead in all_extracted:
                db_lead = DBLead(
                    business_name=lead.extracted_data.business_name,
                    decision_maker_name=lead.extracted_data.decision_maker_name,
                    phone_number=lead.extracted_data.phone_number,
                    email_address=lead.extracted_data.email_address,
                    social_media_link=lead.extracted_data.social_media_link,
                    lead_status=lead.lead_status,
                    confidence_score=lead.confidence_score,
                    reasoning_log=lead.reasoning_log
                )
                db.add(db_lead)
            db.commit()
            logger.info(f"Saved {len(all_extracted)} leads to database ({len(qualified)} qualified, {len(all_extracted) - len(qualified)} other).")
    else:
        logger.warning("No leads extracted — saving raw discovered businesses as unprocessed.")
        raw_biz = final_state.get("raw_businesses", [])
        if raw_biz:
            with SessionLocal() as db:
                for b in raw_biz:
                    db_lead = DBLead(
                        business_name=b.name or "Unknown",
                        phone_number=b.phone or "Not Found",
                        lead_status="Discovered - Awaiting Processing",
                        confidence_score=1,
                        reasoning_log=f"Raw discovery only. Source: {b.source}. URL: {b.website or 'None'}"
                    )
                    db.add(db_lead)
                db.commit()
                logger.info(f"Saved {len(raw_biz)} raw discovered businesses as fallback.")

    output_dir = settings.export.output_dir
    formats = settings.export.formats

    if "json" in formats and qualified:
        export_to_json(qualified, output_dir)
    if "csv" in formats and qualified:
        export_to_csv(qualified, output_dir)

    if enriched:
        enriched_data = [r.model_dump() for r in enriched]
        import json
        import os
        os.makedirs(output_dir, exist_ok=True)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(os.path.join(output_dir, f"enriched_{ts}.json"), "w") as f:
            json.dump(enriched_data, f, indent=2)
        logger.info(f"Exported {len(enriched)} enriched leads to JSON.")

    if errors:
        logger.warning(f"Pipeline finished with {len(errors)} errors.")
        for err in errors:
            logger.warning(f"  {err}")

    logger.info(f"Final result: {len(qualified)} qualified leads (out of {stats.get('discovered_count', 0)} discovered)")


if __name__ == "__main__":
    app()
