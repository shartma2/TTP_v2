from __future__ import annotations

import base64
import io
from graphviz import Digraph
from pypdf import PdfReader, PdfWriter

from typing import Any
from app.utils.logging import get_logger
from app.utils.exceptions import JobNotFoundException, MissingParameterException

from modules.pipeline.schemes._output import PASSModel
from modules.rendering.graphs import build_sbd_digraph, build_sid_digraph

logger = get_logger("modules.rendering.main")

def run(payload: dict[str, Any]) -> dict[str, Any]:
    
    job_id = payload.get("job_id", None)
    source_job_id = payload.get("source_job_id", None)
    source_job_content = payload.get("result", None)


    if not job_id:
        logger.warning("No job_id provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("job_id")
    
    if not source_job_id:
        logger.warning("No source_job_id provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("source_job_id")       

    if not source_job_content:
        logger.warning("No source_job_content provided in payload.", extra={"job_id": job_id})
        raise MissingParameterException("source_job_content")
       
    module = source_job_content.get("module", "N/A")
    status = source_job_content.get("status", "N/A")

    if status != "done":
        logger.error("Job is not ready for export", extra={"job_id": job_id},)
        raise JobNotFoundException(f"Job is not ready for export: {source_job_id}")

    model = PASSModel.model_validate(source_job_content.get("result", {}).get("response"))
    
    logger.info("Running Export module", extra={"job_id": job_id, "format": format})
    svg = _render_model_svg(model)
    pdf = _render_model_pdf(model)
    result = {
        "fileName": "export.pdf",
        "contentType": "application/pdf",
        "sizeBytes": len(pdf),
        "svg": svg,
        "dataBase64": base64.b64encode(pdf).decode("utf-8"),
    }
    return result

def _render_graph_svg(dot: Digraph) -> str:
    return dot.pipe(format="svg")


def _render_graph_pdf(dot: Digraph) -> bytes:
    return dot.pipe(format="pdf")

def _render_model_svg(model: PASSModel) -> dict[str, Any]:
    sid_subjects = {subject.label for subject in model.sid.subjects}

    sid_svg = _render_graph_svg(build_sid_digraph(model.sid))

    sbd_svgs: list[dict[str, str]] = []
    for sbd in model.sbd:
        if sbd.subject not in sid_subjects:
            raise ValueError(f"SBD subject '{sbd.subject}' does not exist in SID subjects")

        sbd_svgs.append({
            "subject": sbd.subject,
            "svg": _render_graph_svg(build_sbd_digraph(sbd)),
        })

    return {
        "sid": sid_svg,
        "sbd": sbd_svgs,
    }

def _render_model_pdf(model: PASSModel) -> bytes:
    sid_subjects = {subject.label for subject in model.sid.subjects}
    writer = PdfWriter()

    sid_pdf = _render_graph_pdf(build_sid_digraph(model.sid))
    sid_reader = PdfReader(io.BytesIO(sid_pdf))
    for page in sid_reader.pages:
        writer.add_page(page)

    for sbd in model.sbd:
        if sbd.subject not in sid_subjects:
            raise ValueError(f"SBD subject '{sbd.subject}' does not exist in SID subjects")

        sbd_pdf = _render_graph_pdf(build_sbd_digraph(sbd))
        sbd_reader = PdfReader(io.BytesIO(sbd_pdf))
        for page in sbd_reader.pages:
            writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()