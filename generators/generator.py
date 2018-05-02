import random
import tops


def scalePlusScale(code1, code2):
    return 'scale('+code1+')+scale('+code2+')'

def multiplyRank(code1, code2):
    return code1+'*rank('+code2+')'

def multiplyRanks(code1, code2):
    return 'rank('+code1+')*rank('+code2+')'


class Generator(object):
    
    def __init__(self):
        self.baseline_fitness = 0.5
        self.max_fitness_fall = 0.7
        self.actions = [
                        scalePlusScale,
                        multiplyRank,
                        multiplyRanks,
                       ]
    
    def get(self, alphaStream):
        history = alphaStream.sending_result_list
        if len(history) < 2:
            if history[-1]['fitness'] < self.baseline_fitness:
                alphaStream.remove_last()
                return self._getRandomAlpha()
            else:
                if history[-2]['fitness'] - history[-1]['fitness'] > self.max_fitness_fall:
                    alphaStream.remove_last()
                return self._improve(history)


    def _improve(self, history):
        alpha = {'code':'', 'params':{}}
        feedback = history[-1]['feedback']
        if feedback['turnover'] > 0.8:
            alpha['code'], alpha['params'] = history[-1]['code'], history[-1]['params']
            alpha['params']['decay'] += 2
        else:
            random_alpha = self._getRandomAlpha()
            new_code = random.choice(self.actions)(random_alpha['code'], alpha['code'])
            new_sending = {
                    'code': new_code,
                    'params': alpha.params,
                    }
            
        return new_sending
    
    def _getRandomAlpha(self):
        return random.choice(tops.uncorr_top())
