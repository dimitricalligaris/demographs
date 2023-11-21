class FileUploadError(Exception):
    def __init__(self, message, filename):
        super().__init__(message)
        self.filename = filename

class FiletypeNotSupportedError(FileUploadError):
    pass

class PlatformNotSupportedError(FileUploadError):
    pass

class DuplicatedFileError(FileUploadError):
    pass

class GenericFileUploadError(FileUploadError):
    pass