from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal

# ----------------------------
# SID
# ----------------------------

class Subject(BaseModel):
    """
    A Subject represented inside an SID
    """
    model_config = ConfigDict(extra="forbid")

    label: str = Field(..., description= "Unique name of the Subject")
    
class SIDMessage(BaseModel):
    """
    Directed communication relation between two subjects.
    """
    model_config = ConfigDict(extra="forbid")

    sender: str = Field(..., description="Name of the Sender subject")
    receiver: str = Field(..., description="Name of the Receiver subject")
    message: str = Field(..., description="Message identifier")

class SID(BaseModel):
    """
    Subject Interaction Diagram consisting of subjects and their message relations.
    """
    model_config = ConfigDict(extra="forbid")

    subjects: List[Subject] = Field(..., description="List of Subject represented in the SID")
    messages: List[SIDMessage] = Field(..., description="List of messages exchanged between subjects")

# ----------------------------
# Enums
# ----------------------------

class StateType(str, Enum):
    SEND = "SendState"
    RECEIVE = "ReceiveState"
    DO = "DoState"

class StateTraits(str, Enum):
    START = "StartState"
    END = "EndState"

class TransitionType(str, Enum):
    DO = "DoTransition"
    SEND = "SendTransition"
    RECEIVE = "ReceiveTransition"

# ----------------------------
# SBD
# ----------------------------

class State(BaseModel):
    """
    State node within a subject's behavior diagram.
    """
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="State identifier unique within the enclosing SBD")
    type: StateType = Field(..., description="State type")
    traits: Optional[StateTraits] = Field(None, description="Specification if the state is and start state, end state or both")
    description: Optional[str] = Field(None, description="Functional description of the state's internal behavior(not the message sent/received next)")

class Transition(BaseModel):
    """
    Directed control-flow relation between two states.
    """
    model_config = ConfigDict(extra="forbid")

    source: str = Field(..., description="Source state name")
    target: str = Field(..., description="Target state name")
    type: TransitionType

    message: Optional[str] = Field(None, description="Referenced message identifier for communication transitions")
    partner: Optional[str] = Field(None, description="Communication partner subject for send/receive transitions")

    guard: Optional[str] = Field(None, description="Optional condition label/expression")

class SBD(BaseModel):
    """
    Subject Behavior Diagram representing the internal behavior of each subject.
    """
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(..., description="Subject name corresponding to an entry in SID.subjects")

    states: List[State] = Field(..., description="Set of states belonging to this subject")
    transitions: List[Transition] = Field(..., description="Directed transitions between states")

# ----------------------------
# Full PASS Model
# ----------------------------
class PASSModel(BaseModel):
    """
    Canonical PASS representation consisting of one SID and multiple SBDs.
    """
    model_config = ConfigDict(extra="forbid")

    sid: SID = Field(..., description="Subject Interaction Diagram")
    sbd: List[SBD] = Field(..., description="Subject Behavior Diagrams (one per subject)")