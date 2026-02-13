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