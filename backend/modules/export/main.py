from __future__ import annotations
from typing import Any
import base64
import json
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
from textwrap import dedent

from app.utils.logging import get_logger
from app.utils.exceptions import InvalidExportFormatException, JobNotFoundException
from modules.pipeline.schemes._output import PASSModel

logger = get_logger("modules.pipeline.main")

def run(payload: dict[str, Any]) -> dict[str, Any]:
    
    job_id = payload.get("job_id", "N/A")
    source_job_id = payload.get("source_job_id", "N/A")
    format = payload.get("format", None)
    job = payload.get("result", None)

    if(not job):
        logger.error("Job not found", extra={"source_job_id": source_job_id})
        raise JobNotFoundException(f"Job not found: {source_job_id}")


    module = job.get("module", "N/A")
    status = job.get("status", "N/A")

    if status != "done":
        logger.error("Job is not ready for export", extra={"job_id": job_id},)
        raise JobNotFoundException(f"Job is not ready for export: {source_job_id}")

    result = job.get("result", {}).get("response")



    logger.info("Running Export module", extra={"job_id": job_id, "format": format})

    match (module, format):
        case (_, ".txt"):
            fileName = "export.txt"
            contentType = "text/plain; charset=utf-8"
            raw_bytes = _to_txt_bytes(result)

        case ("pipeline", ".json"):
            fileName = "export.json"
            contentType = "application/json"
            raw_bytes = _to_json_bytes(result)

        case ("pipeline", ".owl"):
            fileName = "export.owl"
            contentType = "application/rdf+xml"
            raw_bytes = _to_owl_bytes(result)
        
        case (_, _):
            logger.error("Unsupported format", extra={"job_id": job_id, "format": format})
            raise InvalidExportFormatException(f"Unsupported format: {format}")

    result = {
        "fileName": fileName,
        "contentType": contentType,
        "sizeBytes": len(raw_bytes),
        "dataBase64": base64.b64encode(raw_bytes).decode("ascii"),
     }
    
    return {"response": result}

def _to_txt_bytes(data: str) -> bytes:
    if isinstance(data, str):
        return data.encode("utf-8")
    return str(data).encode("utf-8")


def _to_json_bytes(data: str) -> bytes:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    except Exception as e:
        raise ValueError(f"Data cannot be converted to JSON: {e}")



def _to_owl_bytes(data: str, model_label: str = "PASS_Model") -> bytes:

    ABSTRACT = Namespace("http://www.imi.kit.edu/abstract-pass-ont#")
    STANDARD = Namespace("http://www.i2pm.net/standard-pass-ont#")
    BASE = Namespace("http://subjective-me.jimdo.com/s-bpm/processmodels/2025-03-25/Page-1#")
    
    if not isinstance(data, PASSModel):
        try:
            PASSModel.model_validate(data)
        except Exception as e:
            raise ValueError(f"Data cannot be converted to PASSModel for OWL export: {e}")
    

    model = data if isinstance(data, PASSModel) else PASSModel.model_validate(data)

    g = Graph(base=BASE)
    g.bind("abstract-pass-ont", ABSTRACT)
    g.bind("standard-pass-ont", STANDARD)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # Add PASS process model
    model_uri = BASE[model_label]
    g.add((model_uri, RDF.type, STANDARD.PASSProcessModel))
    g.add((model_uri, STANDARD.hasModelComponentID, Literal(f"{model_uri}#Model", datatype=XSD.string)))
    g.add((model_uri, STANDARD.hasModelComponentLabel, Literal(model_label, lang="en")))

    # SID layer
    sid_layer = BASE["SID_1"]
    g.add((sid_layer, RDF.type, ABSTRACT.ModelLayer))
    g.add((sid_layer, STANDARD.hasModelComponentID, Literal("SID_1", datatype=XSD.string)))
    g.add((sid_layer, STANDARD.hasModelComponentLabel, Literal("SID_1", lang="en")))
    g.add((sid_layer, STANDARD.hasPriorityNumber, Literal(1, datatype=XSD.positiveInteger)))
    g.add((model_uri, STANDARD.contains, sid_layer))

    # Subjects
    subject_uri_by_label: dict[str, Any] = {}

    for idx, subject in enumerate(model.sid.subjects, start=2):
        subject_id = f"SID_1_FullySpecifiedSubject_{idx}"
        subject_uri = BASE[subject_id]
        subject_uri_by_label[subject.label.strip().lower()] = subject_uri

        g.add((subject_uri, RDF.type, STANDARD.FullySpecifiedSubject))
        g.add((subject_uri, STANDARD.hasModelComponentID, Literal(subject_id, datatype=XSD.string)))
        g.add((subject_uri, STANDARD.hasModelComponentLabel, Literal(subject.label, lang="en")))
        g.add((subject_uri, STANDARD.hasMaximumSubjectInstanceRestriction, Literal(1, datatype=XSD.integer)))
        g.add((subject_uri, ABSTRACT.hasExecutionCostPerHour, Literal(0.0, datatype=XSD.double)))

        g.add((sid_layer, STANDARD.contains, subject_uri))
        g.add((model_uri, STANDARD.contains, subject_uri))

    # SID messages
    for idx, msg in enumerate(model.sid.messages, start=1):
        sender_uri = subject_uri_by_label[msg.sender.strip().lower()]
        receiver_uri = subject_uri_by_label[msg.receiver.strip().lower()]

        msg_spec_id = f"SID_1_MessageSpecification_{idx}"
        msg_spec_uri = BASE[msg_spec_id]
        g.add((msg_spec_uri, RDF.type, STANDARD.MessageSpecification))
        g.add((msg_spec_uri, STANDARD.hasModelComponentID, Literal(msg_spec_id, datatype=XSD.string)))
        g.add((msg_spec_uri, STANDARD.hasModelComponentLabel, Literal(msg.message, lang="en")))

        payload_id = f"PayloadDefinition_of_{msg_spec_id}"
        payload_uri = BASE[payload_id]
        g.add((payload_uri, RDF.type, OWL.Class))
        g.add((msg_spec_uri, STANDARD.containsPayloadDescription, payload_uri))

        mel_id = f"MessageExchangeList_on_SID_1_StandardMessageConnector_{idx}"
        mel_uri = BASE[mel_id]
        conn_id = f"SID_1_StandardMessageConnector_{idx}"
        conn_uri = BASE[conn_id]

        g.add((mel_uri, RDF.type, STANDARD.MessageExchangeList))
        g.add((mel_uri, STANDARD.hasModelComponentID, Literal(mel_id, datatype=XSD.string)))
        g.add((mel_uri, STANDARD.hasModelComponentLabel, Literal(conn_id, lang="en")))
        g.add((mel_uri, STANDARD.contains, msg_spec_uri))

        g.add((conn_uri, RDF.type, STANDARD.StandardMessageConnector))
        g.add((conn_uri, STANDARD.hasSender, sender_uri))
        g.add((conn_uri, STANDARD.hasReceiver, receiver_uri))
        g.add((conn_uri, STANDARD.hasMessageType, msg_spec_uri))
        g.add((mel_uri, STANDARD.contains, conn_uri))

        for parent in (sid_layer, model_uri):
            g.add((parent, STANDARD.contains, mel_uri))
            g.add((parent, STANDARD.contains, msg_spec_uri))
            g.add((parent, STANDARD.contains, conn_uri))

    # SBDs
    for sbd_index, sbd in enumerate(model.sbd, start=1):
        subject_uri = subject_uri_by_label.get(sbd.subject.strip().lower())
        if subject_uri is None:
            raise ValueError(f"SBD subject '{sbd.subject}' not found in SID.subjects")

        subject_suffix = str(subject_uri).split("_")[-1]
        sbd_id = f"SBD_{sbd_index}_SID_1_FullySpecifiedSubject_{subject_suffix}"
        sbd_uri = BASE[sbd_id]

        g.add((sbd_uri, RDF.type, STANDARD.SubjectBehavior))
        g.add((sbd_uri, STANDARD.hasModelComponentID, Literal(sbd_id, datatype=XSD.string)))
        g.add((sbd_uri, STANDARD.hasModelComponentLabel, Literal(f"SBD: {sbd.subject}", lang="en")))
        g.add((sbd_uri, STANDARD.hasPriorityNumber, Literal(sbd_index, datatype=XSD.positiveInteger)))

        g.add((subject_uri, STANDARD.hasBehavior, sbd_uri))
        g.add((sid_layer, STANDARD.contains, sbd_uri))
        g.add((model_uri, STANDARD.contains, sbd_uri))

        # States
        state_uri_by_name: dict[str, Any] = {}

        for state_index, state in enumerate(sbd.states, start=1):
            state_id = f"SBD_{sbd_index}_{state.type.value}_{state_index}"
            state_uri = BASE[state_id]
            state_uri_by_name[state.name.strip()] = state_uri

            g.add((state_uri, RDF.type, STANDARD[state.type.value]))
            g.add((state_uri, STANDARD.hasModelComponentID, Literal(state_id, datatype=XSD.string)))
            g.add((state_uri, STANDARD.hasModelComponentLabel, Literal(state.name, lang="en")))

            if state.description:
                g.add((state_uri, STANDARD.hasComment, Literal(state.description, lang="en")))

            if state.traits:
                g.add((state_uri, RDFS.comment, Literal(f"Trait: {state.traits.value}", lang="en")))

            g.add((sbd_uri, STANDARD.contains, state_uri))

        # Transitions
        for transition_index, transition in enumerate(sbd.transitions, start=1):
            source_uri = state_uri_by_name.get(transition.source)
            target_uri = state_uri_by_name.get(transition.target)

            if source_uri is None:
                raise ValueError(f"Transition source '{transition.source}' not found in SBD '{sbd.subject}'")
            if target_uri is None:
                raise ValueError(f"Transition target '{transition.target}' not found in SBD '{sbd.subject}'")

            trans_id = f"SBD_{sbd_index}_{transition.type.value}_{transition_index}"
            trans_uri = BASE[trans_id]

            g.add((trans_uri, RDF.type, STANDARD[transition.type.value]))
            g.add((trans_uri, STANDARD.hasModelComponentID, Literal(trans_id, datatype=XSD.string)))
            g.add((trans_uri, STANDARD.hasSourceState, source_uri))
            g.add((trans_uri, STANDARD.hasTargetState, target_uri))

            label_parts: list[str] = []

            if transition.message:
                label_parts.append(f"Msg: {transition.message}")
            if transition.partner:
                if transition.type.value == "SendTransition":
                    label_parts.append(f"To: {transition.partner}")
                elif transition.type.value == "ReceiveTransition":
                    label_parts.append(f"From: {transition.partner}")
                else:
                    label_parts.append(f"Partner: {transition.partner}")
            if transition.guard:
                label_parts.append(f"Guard: {transition.guard}")

            transition_label = "\n".join(label_parts) if label_parts else "Continue Process"
            g.add((trans_uri, STANDARD.hasModelComponentLabel, Literal(transition_label, lang="en")))

            g.add((sbd_uri, STANDARD.contains, trans_uri))

    # Example class retained from old code
    dm_class = BASE["VisioShapesInternalDataMappingFunction"]
    g.add((dm_class, RDF.type, OWL.Class))
    g.add((dm_class, RDFS.subClassOf, STANDARD.DataMappingFunction))

    xml_body = g.serialize(format="application/rdf+xml")

    entities = dedent("""\
        <!DOCTYPE rdf:RDF [
            <!ENTITY owl "http://www.w3.org/2002/07/owl#" >
            <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#" >
            <!ENTITY rdfs "http://www.w3.org/2000/01/rdf-schema#" >
            <!ENTITY abstract-pass-ont "http://www.imi.kit.edu/abstract-pass-ont#" >
            <!ENTITY standard-pass-ont "http://www.i2pm.net/standard-pass-ont#" >
            <!ENTITY rdf "http://www.w3.org/1999/02/22-rdf-syntax-ns#" >
        ]>
    """)

    xml_body_nohead = "\n".join(xml_body.splitlines()[1:])
    xml = f'<?xml version="1.0"?>\n{entities}\n{xml_body_nohead}'
    bytes = str(xml).encode("utf-8")


    return bytes