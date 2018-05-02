import numpy as np
from numpy import random
from numpy.random import randint

short_name = 'first_gen'

class AlphaGenerator(object):
    def __init__(self, first_alphas, limit=np.inf):
        self.alphas = first_alphas
        self.counter = 0
        self.limit = limit


    def __iter__(self):
        return self


    def _changeNums(self, alpha):
        alpha += ' '
        num = ''
        new_alpha = []
        for c in alpha:
            if c == '.' or c.isdigit():
                num += c
            elif num != '':
                if '.' in num:
                    mlt = 0.5 + 0.7*random.rand(1)[0]
                    try:
                        new_num = str(mlt*float(num))
                        new_alpha += [new_num]
                    except:
                        new_alpha += [num]
                else:
                    new_alpha += [num]
                new_alpha += [c]
                num = ''
            else:
                new_alpha += [c]
                num = ''
        return ''.join(new_alpha).strip()


    def _mixAlphas(self, alpha1, alpha2):
        is_rank_prod = random.rand(1)[0] < 0.1
        if is_rank_prod:
            return 'rank('+alpha1+')*rank('+alpha2+')'
        al = random.rand(1)[0]
        return str(al)+'*'+alpha1+'+'+str(1-al)+'*'+alpha2


    def _changeAlpha(self, alpha):
        is_rank = random.rand(1)[0] < 0.4
        is_scale = random.rand(1)[0] < 0.5
        alpha = self._changeNums(alpha)
        if is_rank:
            return 'rank('+alpha+')'
        elif is_scale:
            return 'scale('+alpha+')'
        else:
            return alpha
   
    
    def next(self):
        if self.counter >= self.limit:
            raise StopIteration()
        self.counter += 1

        i = randint(0, len(self.alphas))
        j = randint(0, len(self.alphas))
        self.alphas  += [self._mixAlphas(self._changeAlpha(self.alphas[i]),
                                       self._changeAlpha(self.alphas[j]))]
        return self.alphas[-1]
    
    
f = open('iter0alphas')
alphas = [line for line in f.readlines()][0:10]
alpha_generator = AlphaGenerator(alphas)

def get():
    for alpha in alpha_generator:
        yield {
            'code': alpha,
            'params_info': {
                'delay': ['0', '1'],
                'decay': ['7', '4', '1'],
                'univid': ['TOP2000', 'TOP200'],
                'opneut': ['Subindustry', 'Market']
            }
        }
