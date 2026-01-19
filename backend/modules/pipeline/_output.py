from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal

class StateType(str, Enum):
    SEND = "SendState"
    RECEIVE = "ReceiveState"
    DO = "DoState"

class SIDMessage(BaseModel):
    """
    Minimal SID message relation:
    sender -> receiver : message_name
    """
    model_config = ConfigDict(extra="allow")

    sender: str = Field(..., description="Sender subject")
    receiver: str = Field(..., description="Receiver subject")
    message: str = Field(..., description="Message content")

class SID(BaseModel):
    """
    Minimal SID: subjects + message exchanges.
    Subjects can be derived from messages, but we allow an explicit list
    to keep the output simple and rendering-friendly.
    """
    model_config = ConfigDict(extra="allow")

    subjects: List[str] = Field(..., description="List of subjects involved")
    messages: List[SIDMessage] = Field(..., description="List of messages exchanged between subjects")

class SendBinding(BaseModel):
    """
    For SendState: who is the receiver and what message is sent.
    """
    model_config = ConfigDict(extra="allow")

    to: str = Field(..., description="Receiver subject name")
    message: str = Field(..., description="Message name/type (must exist in SID)")


class ReceiveBinding(BaseModel):
    """
    For ReceiveState: who is the sender and what message is expected.
    """
    model_config = ConfigDict(extra="allow")

    from_: str = Field(..., alias="from", description="Sender subject name")
    message: str = Field(..., description="Message name/type (must exist in SID)")


class FunctionBinding(BaseModel):
    """
    For FunctionState: minimal internal action description.
    """
    model_config = ConfigDict(extra="allow")

    description: Optional[str] = Field(None, description="Short description of internal work")


class State(BaseModel):
    """
    Minimal state node. Uses a name that is unique within the subject's SBD.
    The type determines which binding object is expected.
    """
    model_config = ConfigDict(extra="allow")

    name: str = Field(..., description="Unique state name within this SBD (used for transitions)")
    type: StateType = Field(..., description="State type")

    send: Optional[SendBinding] = None
    receive: Optional[ReceiveBinding] = None
    function: Optional[FunctionBinding] = None

class Transition(BaseModel):
    """
    Minimal directed edge between states.
    """
    model_config = ConfigDict(extra="allow")

    source: str = Field(..., description="Source state name")
    target: str = Field(..., description="Target state name")

    guard: Optional[str] = Field(None, description="Optional condition label/expression")

class SubjectBehavior(BaseModel):
    """
    One SBD per subject.
    """
    model_config = ConfigDict(extra="allow")

    subject: str = Field(..., description="Subject name (must exist in SID.subjects)")
    start: str = Field(..., description="Name of the start state for this subject")

    states: List[State] = Field(..., description="States for this subject")
    transitions: List[Transition] = Field(..., description="Transitions between states")

class PASSModel(BaseModel):
    """
    Minimal canonical output: SID + list of SBDs.
    This object is intended to be stable regardless of internal pipeline.
    """
    model_config = ConfigDict(extra="allow")

    sid: SID = Field(..., description="Subject Interaction Diagram")
    sbd: List[SubjectBehavior] = Field(..., description="Subject Behavior Diagrams (one per subject)")