import os
try:
    import dspy  # type: ignore
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

def configure_dspy(model_name: str):
    """
    Configures the DSPy language model with the given model name.
    If DSPy is available, creates a new language model instance and sets dspy.settings.lm.
    Returns the language model instance.
    """
    if DSPY_AVAILABLE:
        lm = dspy.LM(model_name)
        dspy.settings.configure(lm=lm)
        return lm
    return None
