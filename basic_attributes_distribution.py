
class BasicAttributesDistribution:
    def __init__(self, parent=None):
        self.parent = parent

    def __getattr__(self, name):
        if self.parent is not None and hasattr(self.parent, name):
            return getattr(self.parent, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def with_color_distribution(self, color_distribution):
        self.color_distribution = color_distribution
        return self
    
