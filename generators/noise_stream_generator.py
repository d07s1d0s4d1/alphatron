import abc
import numpy as np
from base_generator import AbstractAlphaStreamGenerator
from numpy.random import randint

logger = logging.getLogger(__name__)

class NoiseStreamGenerator(AbstractAlphaStreamGenerator):

    """
        Add noise to last alpha in stream to reduce correlation
    """ 
        
    def get(self):
        code1 = self.alpha_stream.sending_list[-1].get_params()['code']
        a, b = randint(10**7), randint(10**7)
        return "{}*scale({}*rank(Correlation(close, open, 2))+{}*rank(adv20))".format(0.2, a, b)
        
        
        
        