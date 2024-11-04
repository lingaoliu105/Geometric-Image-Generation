

from abc import ABC, abstractmethod


class ImageGenerator(ABC):
    @abstractmethod
    def generate(self):
        pass