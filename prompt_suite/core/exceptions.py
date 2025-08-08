"""
Excepciones personalizadas para Prompt Suite
"""


class PromptSuiteError(Exception):
    """Excepción base para Prompt Suite"""
    pass


class ValidationError(PromptSuiteError):
    """Error de validación de datos"""
    pass


class TemplateValidationError(ValidationError):
    """Error de validación de template"""
    pass


class MissingParameterError(TemplateValidationError):
    """Error cuando falta un parámetro requerido"""
    pass


class ExtraParameterError(TemplateValidationError):
    """Error cuando se proporciona un parámetro extra"""
    pass


class ParameterError(TemplateValidationError):
    """Error general de parámetros"""
    pass


class PromptNotFoundError(PromptSuiteError):
    """Error cuando no se encuentra un prompt"""
    pass


class ModelNotFoundError(PromptSuiteError):
    """Error cuando no se encuentra un modelo en un prompt"""
    pass


class DefaultModelError(PromptSuiteError):
    """Error relacionado con el modelo por defecto"""
    pass


class HistoryError(PromptSuiteError):
    """Error relacionado con el historial"""
    pass


class FileFormatError(PromptSuiteError):
    """Error de formato de archivo"""
    pass
