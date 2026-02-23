from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Tuple, Dict

from modules.pipeline.schemes._output import (PASSModel, TransitionType, StateTraits, StateType)

def run(input: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    issues += _validate_sid(input)
    return issues

@dataclass(frozen=True)
class Issue:
    code: str
    message: str
    path: Optional[str] = None


    


def _validate_sid(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    labels = [s.label.strip() for s in model.sid.subjects]
    #check for empty labels
    for idx, l in enumerate(labels):
        if not isinstance(l, str) or not l.strip():
            issues.append(Issue(
                code="SID_SUBJECT_EMPTY",
                message="Subject.label must not be empty",
                path=f"sid.subjects[{idx}].label"
            ))
    
    #check for duplicates
    if len(set(labels)) != len(labels):
        issues.append(Issue(
            code="SID_SUBJECT_DUPLICATE",
            message="Duplicate subject label"
        ))

    #check if message rules are applied 
    for idx, m in enumerate(model.sid.messages):
        if m.sender == m.receiver:
            issues.append(Issue(
                code="SID_MESSAGE_LOOP",
                message="SIDMessage.sender and receiver must be different.",
                path=f"sid.messages[{idx}]"
            ))
        if m.sender not in labels:
            issues.append(Issue(
                code="SID_MESSAGE_UNKNOWN_SENDER",
                message=f"Sender '{m.sender}' is not declared in sid.subjects.",
                path=f"sid.messages[{idx}].sender",
            ))
        if m.receiver not in labels:
            issues.append(Issue(
                code="SID_MESSAGE_UNKNOWN_RECEIVER",
                message=f"Receiver '{m.receiver}' is not declared in sid.subjects.",
                path=f"sid.messages[{idx}].receiver",
            ))
        if not isinstance(m.message, str) or not m.message.strip():
            issues.append(Issue(
                code="SID_MESSAGE_EMPTY",
                message="SIDMessage.message must not be empty.",
                path=f"sid.messages[{idx}].message",
            ))
    return issues

def _validate_sbd_structure(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []
