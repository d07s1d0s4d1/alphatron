#import simple_generator
import itertools
import tops
import tree_generator as tg
import logging
import copy
import numpy as np
import parser as ps

logger = logging.getLogger(__name__)


def plus(code1, code2):
    if not code1.startswith("scale"):
        code1 = 'scale('+code1+')'
    if not code2.startswith("scale"):
        code2 = 'scale('+code1+')'
    return code1+'+'+code2


def multiplyRank(code1, code2):
    return 'scale(rank('+code1+')*rank('+code2+'))'


def signedPower(code1, code2):
    pw = np.random.uniform(0.3, 3)
    return 'signedpower({},{})'.format(code1, pw)


def treeCode(code1, code2):
    try:
        node1, node2 = tg.dict_tree(ps.parse(code1)), \
                        tg.dict_tree(ps.parse(code2))
        check_node = copy.deepcopy(node1)
        tg.mix_trees(node1, node2)
        new_code, check_code = tg.compile_alpha(node1), tg.compile_alpha(check_node)
        assert(new_code != check_code)
        return new_code
    except Exception as e:
        logger.info("treeCode failed on alphas {}, {}".format(code1, code2))
        return plus(code1, code2)


def extract_simple_code(code):
    if ';' in code:
        return code.split(';')[0].split('=')[1]
    else:
        return code

def truncateCode(code):
    try:
        node = tg.dict_tree(ps.parse(code))
        node = tg.get_subtree(node)
        new_code = tg.compile_alpha(node)
        return '(' + new_code + ')'
    except Exception as e:
        logger.info("Getting subtree failed on alpha {}".format(code))
        return code
    

def mixCondition(code1, code2):
    cond = "rank(scale({})+scale({}))".format(code1, code2)
    return "x1={};x2={};cond={};cond>delay(cond, 50)?x1:x2".format(code1, code2, cond)



class AlphaStreamGenerator(object):
    def __init__(self, alpha_stream):
        self.alpha_stream = alpha_stream
        self.truncateAlpha = truncateCode
        self.actions = [
                        plus,
                        multiplyRank,
                        signedPower,
                        treeCode,
                        mixCondition,
                       ]

    def get(self):
        code, params = extract_simple_code(self.alpha_stream.sending_list[-1].get_params()['code']), \
                       self.alpha_stream.sending_list[-1].get_params()['params']
        logger.info("input code: {}".format(code))
        gen = np.random.choice(self.actions, p=len(self.actions)*[1.0/len(self.actions)])
        rand_alpha = self.__getRandomAlpha__()
        
        new_code = gen(extract_simple_code(self.__getRandomAlpha__()["code"]), code)
        logger.info("output code: {}".format(new_code))
        return {
            "alpha": {
                    "code": new_code,
                    "params": params,
                },
            "metadata": {
                    "generator": gen.__name__,
                    "added_alpha": rand_alpha["sendingID"],
            }
        }



    def __getRandomAlpha__(self):
        return np.random.choice(tops.uncorr_top())
