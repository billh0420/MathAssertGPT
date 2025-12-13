# from shared.classes
# step_logger.py

from abc import abstractmethod, ABC


class StepLogger(ABC):

    @abstractmethod
    def log_step(self, step: int, max_examples: int):
        pass