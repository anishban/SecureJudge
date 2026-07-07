from app.constants import MAX_SOURCE_CODE_LENGTH, SUPPORTED_LANGUAGES

def validate_job_submission(data):
    if data is None:
        return False, "request body must be valid json"
    
    language = data.get("language")
    source_code = data.get("source_code")

    if language is None:
        return False, "language is required"
    if source_code is None:
        return False, "source code is required"
    if not isinstance(source_code, str):
        return False, "source code must be a string"
    if not isinstance(language, str):
        return False, "language must be a string"
    language = language.strip().lower()
    if language == "":
        return False, "language cannot be empty"
    if source_code.strip() == "":
        return False, "source code cannot be empty"
    if language not in SUPPORTED_LANGUAGES:
        return False, f"Unsupported Language: {language}"
    if len(source_code)> MAX_SOURCE_CODE_LENGTH:
        return False, f"Source code cannot exceed {MAX_SOURCE_CODE_LENGTH} characters"
    return True, None
    