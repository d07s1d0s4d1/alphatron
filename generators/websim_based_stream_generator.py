import abc
import numpy as np
from base_generator import AbstractAlphaStreamGenerator
from numpy.random import randint

logger = logging.getLogger(__name__)

def multiplyRank(code1, code2):
    return 'scale(rank('+code1+')*rank('+code2+'))'

actions = [multiplyRank]

class WebsimStreamGenerator(AbstractAlphaStreamGenerator):

    """
        rank product and other mixes based on websim functions
    """
        
    def get(self):
        code1 = self.alpha_stream.sending_list[-1].get_params()['code']
        code2 = self.__getRandomAlpha__()['code']
        action = np.random.choice(actions)
        return action(code1, code2)