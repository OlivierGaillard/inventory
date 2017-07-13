from django.core.exceptions import ValidationError

def validate_marque(value):
    """Raise a validation error if the marque_ref field
    is empty. Otherwise this field must be filled.
    Finally...NOT the right the place to implement it.
    The natural place is in the formś *clean* method.
    """
    pass