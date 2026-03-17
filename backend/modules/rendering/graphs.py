from __future__ import annotations

import re
from graphviz import Digraph

from app.models.PASSModel import (
    SID,
    SBD,
    State,
    Transition,
    StateType,
    StateTraits,
    TransitionType,
)

def _safe_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())
    if not cleaned:
        cleaned = "node"
    if cleaned[0].isdigit():
        cleaned = f"n_{cleaned}"
    return cleaned


def _state_fillcolor(state: State) -> str:
    if state.type == StateType.SEND:
        return "lightgreen"
    if state.type == StateType.RECEIVE:
        return "lightpink"
    return "lightyellow"


def _state_shape(state: State) -> str:
    if state.traits == StateTraits.END:
        return "doubleoctagon"
    return "box"


def _build_state_label(state: State) -> str:
    lines = [state.name, f"[{state.type.value}]"]
    if state.traits is not None:
        lines.append(f"Trait: {state.traits.value}")
    if state.description:
        lines.append(state.description)
    return "\n".join(lines)


def _build_transition_label(transition: Transition) -> str:
    parts: list[str] = []

    if transition.type == TransitionType.SEND:
        parts.append("send")
    elif transition.type == TransitionType.RECEIVE:
        parts.append("receive")
    else:
        parts.append("do")

    if transition.partner:
        parts.append(f"partner: {transition.partner}")
    if transition.message:
        parts.append(f"msg: {transition.message}")
    if transition.guard:
        parts.append(f"guard: {transition.guard}")

    return "\n".join(parts)


def build_sid_digraph(sid: SID) -> Digraph:
    dot = Digraph(name="SID")
    dot.attr(rankdir="LR", splines="polyline", dpi="300")
    dot.attr("graph", fontsize="14", label="SID", labelloc="t")
    dot.attr("node", shape="box", style="filled", fillcolor="lightblue", fontname="Helvetica")
    dot.attr("edge", fontname="Helvetica")

    subject_names = {subject.label for subject in sid.subjects}

    for subject in sid.subjects:
        dot.node(_safe_id(subject.label), label=subject.label)

    for msg in sid.messages:
        if msg.sender not in subject_names:
            raise ValueError(f"SID message sender '{msg.sender}' is not declared in sid.subjects")
        if msg.receiver not in subject_names:
            raise ValueError(f"SID message receiver '{msg.receiver}' is not declared in sid.subjects")

        dot.edge(_safe_id(msg.sender), _safe_id(msg.receiver), label=msg.message)

    return dot


def build_sbd_digraph(sbd: SBD) -> Digraph:
    dot = Digraph(name=f"SBD_{_safe_id(sbd.subject)}")
    dot.attr(rankdir="LR", splines="polyline", dpi="300")
    dot.attr("graph", fontsize="14", label=f"SBD: {sbd.subject}", labelloc="t")
    dot.attr("edge", fontname="Helvetica")

    state_names = {state.name for state in sbd.states}

    for state in sbd.states:
        dot.node(
            _safe_id(state.name),
            label=_build_state_label(state),
            shape=_state_shape(state),
            style="filled",
            fillcolor=_state_fillcolor(state),
            fontname="Helvetica",
        )

    for transition in sbd.transitions:
        if transition.source not in state_names:
            raise ValueError(
                f"SBD '{sbd.subject}' transition source '{transition.source}' is not declared in sbd.states"
            )
        if transition.target not in state_names:
            raise ValueError(
                f"SBD '{sbd.subject}' transition target '{transition.target}' is not declared in sbd.states"
            )

        dot.edge(
            _safe_id(transition.source),
            _safe_id(transition.target),
            label=_build_transition_label(transition),
        )

    return dot