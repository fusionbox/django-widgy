from django.core.exceptions import ValidationError


class InvalidOperation(ValidationError):
    pass


class InvalidTreeMovement(InvalidOperation):
    """
    Inherits from ``django.core.exceptions.ValidationError``.

    Base exception for all erroneous node restructures.
    """
    def __init__(self, message):
        # If we don't do this, there won't be a message_dict.
        super(InvalidTreeMovement, self).__init__({'message': [message]})


class RootDisplacementError(InvalidTreeMovement):
    """
    Raise when trying to add siblings to a root node.
    """


class ParentChildRejection(InvalidTreeMovement):
    """
    General exception for when a child rejects a parent or vice versa.
    """


class ParentWasRejected(ParentChildRejection):
    """
    Raised by child to reject the requested parent.
    """


class ChildWasRejected(ParentChildRejection):
    """
    Raised by parents to reject children that don't belong.
    """


class MutualRejection(ParentWasRejected, ChildWasRejected):
    """
    For instances where both child and parent reject the movement request.
    """
