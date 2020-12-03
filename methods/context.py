import abc


class Context(abc.ABC):
    @abc.abstractmethod
    def get_next_backend(self):
        """
        get the next backend based on the context
        """

    @abc.abstractmethod
    def cleanup(self):
        """
        clean up after the request has been forwarded
        """
