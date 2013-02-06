from widgy.models import Node

class PreventProblemsMiddleware(object):
    """
    Checks if there are any 'problems' (inconsitensies in the widgy tree)
    after every request. If used with TransactionMiddleware, it will
    prevent problems from being committed by raising an exception. Useful
    to turn on during development so you know right away if your code
    corrupts the tree. It does an absurd number of queries though,
    so probably not something to leave on all the time.
    """

    def get_problems(self):
        return Node.find_problems() + Node.find_widgy_problems()

    def process_response(self, request, response):
        problems = self.get_problems()
        assert not any(problems), "There are some problems: %s" % (problems,)
        return response
