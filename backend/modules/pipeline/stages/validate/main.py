from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Set, Tuple, Dict

from app.models.PASSModel import (PASSModel, TransitionType, StateTraits, StateType)

def run(input: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    issues += _validate_sid(input)
    issues += _validate_sbds(input)
    issues += _validate_transitions(input)
    issues += _cross_check_messages(input)
    issues += _validate_start_end(input)
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

def _validate_sbds(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    sid_subjects = {s.label.strip() for s in model.sid.subjects if isinstance(s.label, str)}
    sbd_subjects = [b.subject.strip() if isinstance(b.subject, str) else b.subject for b in model.sbd]

    for idx, subj in enumerate(sbd_subjects):
        if subj not in sid_subjects:
            issues.append(Issue(
                code="SBD_SUBJECT_NOT_IN_SID",
                message=f"SBD.subject '{subj}' is not declared in sid.subjects.",
                path=f"sbd[{idx}].subject",
            ))
    
    if len(set(sbd_subjects)) != len(sbd_subjects):
        issues.append(Issue(
            code="SBD_SUBJECT_DUPLICATE",
            message="Duplicate SBD subject"
        )) 

    for idx_sbd, sbd in enumerate(model.sbd):
        state_names = [st.name for st in sbd.states]
        if len(set(state_names)) != len(state_names):
            issues.append(Issue(
                code="SBD_STATE_DUPLICATE",
                message=f"Duplicate State within SBD({sbd.subject})",
                path=f"sbd[{idx_sbd}]",
            ))         
       
        state_names_set = set(state_names)
        for idx_t, t in enumerate(sbd.transitions):
            if t.source not in state_names_set:
                issues.append(Issue(
                    code="TRANSITION_SOURCE_UNKNOWN",
                    message=f"Transition.source '{t.source}' not found in states of SBD({sbd.subject}).",
                    path=f"sbd[{idx_sbd}].transitions[{idx_t}].source",
                ))
            if t.target not in state_names_set:
                issues.append(Issue(
                    code="TRANSITION_TARGET_UNKNOWN",
                    message=f"Transition.target '{t.target}' not found in states of SBD({sbd.subject}).",
                    path=f"sbd[{idx_sbd}].transitions[{idx_t}].target",
                ))
    
    return issues

def _validate_transitions(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    for idx_sbd, sbd in enumerate(model.sbd):
        for idx_t, t in enumerate(sbd.transitions):
            path = f"sbd[{idx_sbd}].transitions[{idx_t}]"
            if t.type == TransitionType.DO:
                if t.message is not None or t.partner is not None:
                    issues.append(Issue(
                        code="DO_TRANSITION_HAS_MESSAGE",
                        message="DoTransition must not define message or partner.",
                        path=path,
                    ))
            else: 
                if t.message is None or not str(t.message).strip():
                    issues.append(Issue(
                        code="COMM_TRANSITION_MISSING_MESSAGE",
                        message=f"{t.type.value} requires a non-empty message.",
                        path=f"{path}.message",
                    ))
                if t.partner is None or not str(t.partner).strip():
                    issues.append(Issue(
                        code="COMM_TRANSITION_MISSING_PARTNER",
                        message=f"{t.type.value} requires a non-empty partner.",
                        path=f"{path}.partner",
                    ))
    return issues

def _cross_check_messages(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    sid_msgs: Set[Tuple[str, str, str]] = set()
    for m in model.sid.messages:
        sid_msgs.add((m.sender, m.receiver, m.message))

    sid_subjects = {s.label.strip() for s in model.sid.subjects if isinstance(s.label, str)}

    for idx_sbd, sbd in enumerate(model.sbd):
        subj = sbd.subject
        for idx_t, t in enumerate(sbd.transitions):
            if t.type == TransitionType.SEND:
                triple = (subj, t.partner, t.message)
                if not t.partner or not t.message:
                    continue
                if triple not in sid_msgs:
                    issues.append(Issue(
                        code="SEND_NOT_IN_SID",
                        message=f"SendTransition ({subj} -> {t.partner} : {t.message}) not declared in SID.messages.",
                        path=f"sbd[{idx_sbd}].transitions[{idx_t}]",
                    ))
                if t.partner not in sid_subjects:
                    issues.append(Issue(
                        code="SEND_PARTNER_NOT_IN_SID",
                        message=f"SendTransition partner '{t.partner}' not declared as SID subject.",
                        path=f"sbd[{idx_sbd}].transitions[{idx_t}].partner",
                    ))
            elif t.type == TransitionType.RECEIVE:
                triple = (t.partner, subj, t.message)
                if not t.partner or not t.message:
                    continue
                if triple not in sid_msgs:
                    issues.append(Issue(
                        code="RECEIVE_NOT_IN_SID",
                        message=f"ReceiveTransition ({t.partner} -> {subj} : {t.message}) not declared in SID.messages.",
                        path=f"sbd[{idx_sbd}].transitions[{idx_t}]",
                    ))
                if t.partner not in sid_subjects:
                    issues.append(Issue(
                        code="RECEIVE_PARTNER_NOT_IN_SID",
                        message=f"ReceiveTransition partner '{t.partner}' not declared as SID subject.",
                        path=f"sbd[{idx_sbd}].transitions[{idx_t}].partner",
                    ))

    return issues

def _validate_start_end(model: PASSModel) -> List[Issue]:
    issues: List[Issue] = []

    for idx_sbd, sbd in enumerate(model.sbd):
        start_idxs = [idx_st for idx_st, st in enumerate(sbd.states) if st.traits == StateTraits.START]
        if len(start_idxs) != 1:
            issues.append(Issue(
                code="START_STATE_COUNT",
                message=f"SBD({sbd.subject}) should have exactly 1 start state (found {len(start_idxs)}).",
                path=f"sbd[{idx_sbd}].states",
            ))

        outgoing_count: Dict[str, int] = {}
        for t in sbd.transitions:
            outgoing_count[t.source] = outgoing_count.get(t.source, 0) + 1

        for idx_st, st in enumerate(sbd.states):
            if st.traits == StateTraits.END and outgoing_count.get(st.name, 0) > 0:
                issues.append(Issue(
                    code="END_STATE_HAS_OUTGOING",
                    message=f"End state '{st.name}' in SBD({sbd.subject}) must not have outgoing transitions.",
                    path=f"sbd[{idx_sbd}].states[{idx_st}]",
                ))

    return issues        