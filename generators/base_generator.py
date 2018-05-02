import abc

class AbstractAlphaStreamGenerator(object):
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def __init__(self, alpha_stream):
        self.alpha_stream = alpha_stream

    
    @abc.abstractmethod
    def get(self):
        """Make new alpha based on previous one"""
        return


    @abc.abstractmethod
    def __getRandomAlpha__(self):
        """Retriev random alpha from top""""
        return np.random.choice(tops.uncorr_top())