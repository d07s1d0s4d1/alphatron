import abc
import tree_generator as tg
from base_generator import AbstractAlphaStreamGenerator

logger = logging.getLogger(__name__)

class TreeStreamGenerator(AbstractAlphaStreamGenerator):

    """
        Mix alpha with random alpha as two ariphmetic trees,
        if mix is unsucessfull then returns sum of two alphas
    """

    def get(self):
        code1 = self.alpha_stream.sending_list[-1].get_params()['code']
        code2 = self.__getRandomAlpha__()['code']

        try:
            node1, node2 = tg.dict_tree(tg.expr.parseString(code1)), \
                            tg.dict_tree(tg.expr.parseString(code2))
            check_node = copy.deepcopy(node1)
            tg.mix_trees(node1, node2)
            new_code, check_code = tg.compile_alpha(node1), tg.compile_alpha(check_node)
            assert(new_code != check_code)
            return new_code
        except Exception as e:
            logger.info("treeCode failed on alphas {}, {}".format(code1, code2))
            return "{}+{}".format(code1, code2)