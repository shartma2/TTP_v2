class JobError(Exception):
    """
    Base class for all job-level errors.
    Raising this means: the job failed for a controlled/business reason.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class MissingMessageException(JobError):
    """Raised if the Input is missing."""

class ModelValidationException(JobError):
    """Raised if a model validation fails"""

class InvalidPASSModelException(ModelValidationException):
    """Generated output could not be validated as PASSModel."""