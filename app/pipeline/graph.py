from langgraph.graph import END, StateGraph

from app.config.settings import Settings
from app.pipeline.nodes import PipelineNodes
from app.pipeline.state import PipelineState


def build_graph(settings: Settings) -> StateGraph:
    nodes = PipelineNodes(settings)

    workflow = StateGraph(PipelineState)

    workflow.add_node("discover", nodes.discover_node)
    workflow.add_node("dedup", nodes.dedup_node)
    workflow.add_node("qualify", nodes.qualify_node)
    workflow.add_node("analyze", nodes.analyze_node)

    if settings.enrichment.enabled:
        workflow.add_node("enrich", nodes.enrich_node)

    workflow.set_entry_point("discover")

    workflow.add_edge("discover", "dedup")
    workflow.add_edge("dedup", "qualify")
    workflow.add_edge("qualify", "analyze")

    if settings.enrichment.enabled:
        workflow.add_edge("analyze", "enrich")
        workflow.add_edge("enrich", END)
    else:
        workflow.add_edge("analyze", END)

    return workflow.compile()
