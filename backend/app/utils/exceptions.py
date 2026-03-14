class JobError(Exception):
    """
    Base class for all job-level errors.
    Raising this means: the job failed for a controlled/business reason.
    """
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

class MissingParameterException(JobError):
    """Raised if a Input Parameter is missing."""
    def __init__(self, parameter: str):
        self.parameter = parameter
        super().__init__(f"Missing required parameter: '{parameter}'")

class ModelValidationException(JobError):
    """Raised if a model validation fails"""

class InvalidPASSModelException(ModelValidationException):
    """Generated output could not be validated as PASSModel."""

class InvalidExportFormatException(JobError):
    """Raised if the export format is not supported."""

class JobNotFoundException(JobError):
    """Raised if a job with the given ID is not found."""