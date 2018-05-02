import abc
import tree_generator as tg
from base_generator import AbstractAlphaStreamGenerator
import numpy as np
from numpy.random import random

logger = logging.getLogger(__name__)

def random_polynom(x, y):
    a20,a11,a02,a10,a01 = [random() for i in range(5)]
    return "{2}*signedpower({0},2)+{3}*{0}*{1}+{4}*signedpower({1},2)+{5}*{0}+{6}*{1}".format(x,y,a20,a11,a02,a10,a01)

class MonotonousStreamGenerator(AbstractAlphaStreamGenerator):

    """
        Applies polinom with positive coeffitients to last alpha in stream
        and random alpha
    """

    def get(self):
        code1 = self.alpha_stream.sending_list[-1].get_params()['code']
        code2 = self.__getRandomAlpha__()['code']
        return "scale({})".format(random_polynom(code1, code2))
        