from django.core.exceptions import ValidationError


class InvalidTreeMovement(ValidationError):
    """
    Inherits from ``django.core.exceptions.ValidationError``.

    Base exception for all erroneous node restructures.
    """
    pass


class RootDisplacementError(InvalidTreeMovement):
    """
    Raise when trying to add siblings to a root node.
    """
    pass


class ParentChildRejection(InvalidTreeMovement):
    """
    General exception for when a child rejects a parent or vice versa.
    """
    def __init__(self):
        super(ParentChildRejection, self).__init__({'message': self.message})


class BadParentRejection(ParentChildRejection):
    """
    Raised by child to reject the requested parent.
    """
    message = "You can't put me in that"


class BadChildRejection(ParentChildRejection):
    """
    Raised by parents to reject children that don't belong.
    """
    message = "You can't put that in me"


class OhHellNo(BadParentRejection, BadChildRejection):
    """
    For instances where both child and parent reject the movement request.
    """
    message = "Everyone hates everything"
