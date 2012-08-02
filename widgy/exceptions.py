from django.core.exceptions import ValidationError


class InvalidTreeMovement(ValidationError):
    pass


class RootDisplacementError(InvalidTreeMovement):
    pass


class ParentChildRejection(InvalidTreeMovement):
    def __init__(self):
        super(ParentChildRejection, self).__init__({'message': self.message})


class BadParentRejection(ParentChildRejection):
    message = "You can't put me in that"


class BadChildRejection(ParentChildRejection):
    message = "You can't put that in me"


class OhHellNo(BadParentRejection, BadChildRejection):
    message = "Everyone hates everything"
