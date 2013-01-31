from django.core.exceptions import ValidationError


class InvalidOperation(ValidationError):
    pass

class InvalidTreeMovement(InvalidOperation):
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


class ParentWasRejected(ParentChildRejection):
    """
    Raised by child to reject the requested parent.
    """
    message = "This content does not accept being a child of that parent."


class ChildWasRejected(ParentChildRejection):
    """
    Raised by parents to reject children that don't belong.
    """
    message = "The parent does not accept this content as a child."


class MutualRejection(ParentWasRejected, ChildWasRejected):
    """
    For instances where both child and parent reject the movement request.
    """
    message = "Neither the parent or child accept this parent-child relationship."
