from __future__ import annotations
from langchain.tools import tool

from .schemes._tools import RenameSubject, RenameMessage, RenameState, DeleteSubject

def build_tools(model_data: dict):
    @tool(args_schema=RenameSubject)
    def rename_subject(old_name: str, new_name: str) -> str:
        """Rename an existing subject in the PASS model."""
        _rename_subject(model_data, old_name, new_name)
        return f"Subject '{old_name}' renamed to '{new_name}'."

    @tool(args_schema=RenameState)
    def rename_state(subject_name: str, old_name: str, new_name: str) -> str:
        """Rename an existing state within a specific subject."""
        _rename_state(model_data, subject_name, old_name, new_name)
        return f"State '{old_name}' in subject '{subject_name}' renamed to '{new_name}'."

    @tool(args_schema=RenameMessage)
    def rename_message(old_name: str, new_name: str) -> str:
        """Rename an existing message in the PASS model."""
        _rename_message(model_data, old_name, new_name)
        return f"Message '{old_name}' renamed to '{new_name}'."

    @tool(args_schema=DeleteSubject)
    def delete_subject(subject_name: str) -> str:
        """Delete an existing subject from the PASS model."""
        _delete_subject(model_data, subject_name)
        return f"Subject '{subject_name}' deleted."

    return [rename_subject, rename_state, rename_message, delete_subject]

def _rename_subject(model_data: dict, old_name: str, new_name: str) -> bool:
    changed = False

    # SID.subjects[].label
    for subject in model_data.get("sid", {}).get("subjects", []):
        if subject.get("label") == old_name:
            subject["label"] = new_name
            changed = True

    # SID.messages[].sender / receiver
    for message in model_data.get("sid", {}).get("messages", []):
        if message.get("sender") == old_name:
            message["sender"] = new_name
            changed = True
        if message.get("receiver") == old_name:
            message["receiver"] = new_name
            changed = True

    # SBD[].subject and transitions[].partner
    for sbd in model_data.get("sbd", []):
        if sbd.get("subject") == old_name:
            sbd["subject"] = new_name
            changed = True

        for transition in sbd.get("transitions", []):
            if transition.get("partner") == old_name:
                transition["partner"] = new_name
                changed = True

    return changed

def _rename_state(model_data: dict, subject_name: str, old_name: str, new_name: str) -> bool:
    changed = False

    for sbd in model_data.get("sbd", []):
        if sbd.get("subject") != subject_name:
            continue

        # SBD.states[].name
        for state in sbd.get("states", []):
            if state.get("name") == old_name:
                state["name"] = new_name
                changed = True

        # SBD.transitions[].source / target
        for transition in sbd.get("transitions", []):
            if transition.get("source") == old_name:
                transition["source"] = new_name
                changed = True
            if transition.get("target") == old_name:
                transition["target"] = new_name
                changed = True

    return changed

def _rename_message(model_data: dict, old_name: str, new_name: str) -> bool:
    changed = False

    # SID.messages[].message
    for message in model_data.get("sid", {}).get("messages", []):
        if message.get("message") == old_name:
            message["message"] = new_name
            changed = True

    # SBD.transitions[].message
    for sbd in model_data.get("sbd", []):
        for transition in sbd.get("transitions", []):
            if transition.get("message") == old_name:
                transition["message"] = new_name
                changed = True

    return changed

def _delete_subject(model_data: dict, subject_name: str) -> bool:
    changed = False

    sid = model_data.get("sid", {})

    # Remove subject from SID.subjects
    old_subjects = sid.get("subjects", [])
    new_subjects = [subject for subject in old_subjects if subject.get("label") != subject_name]
    if len(new_subjects) != len(old_subjects):
        sid["subjects"] = new_subjects
        changed = True

    # Remove related SID messages
    old_messages = sid.get("messages", [])
    new_messages = [
        message
        for message in old_messages
        if message.get("sender") != subject_name and message.get("receiver") != subject_name
    ]
    if len(new_messages) != len(old_messages):
        sid["messages"] = new_messages
        changed = True

    # Remove matching SBD
    old_sbd = model_data.get("sbd", [])
    new_sbd = [sbd for sbd in old_sbd if sbd.get("subject") != subject_name]
    if len(new_sbd) != len(old_sbd):
        model_data["sbd"] = new_sbd
        changed = True

    # Remove transitions in remaining SBDs that still reference deleted partner
    for sbd in model_data.get("sbd", []):
        old_transitions = sbd.get("transitions", [])
        new_transitions = [
            transition
            for transition in old_transitions
            if transition.get("partner") != subject_name
        ]
        if len(new_transitions) != len(old_transitions):
            sbd["transitions"] = new_transitions
            changed = True

    return changed