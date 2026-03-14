from pydantic import BaseModel, Field

class RenameSubject(BaseModel):
    old_name: str = Field(description="Current name of the subject to rename")
    new_name: str = Field(description="New name for the subject")

class RenameState(BaseModel):
    subject_name: str = Field(description="Name of the subject owning the state")
    old_name: str = Field(description="Current name of the state")
    new_name: str = Field(description="New name of the state")

class RenameMessage(BaseModel):
    old_name: str = Field(description="Current name of the message")
    new_name: str = Field(description="New name for the message")

class DeleteSubject(BaseModel):
    subject_name: str = Field(description="Name of the subject to delete")    