import numpy as np
from numpy import random
import itertools
import params_info_list
import tops
import time


short_name = 'change_consts'

def get():
    while True:
        alphas = [a['code'] for a in random.choice(list(tops.uncorr_top()), 10)]
        for al in alphas:
            yield {
                'code': _changeNums(al),
                'params_info': params_info_list.params_info,
            }
            time.sleep(5)


def _changeNums(alpha):
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
