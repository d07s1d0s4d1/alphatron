from numpy import random
import copy
import numpy as np
import itertools
import params_info_list
import tops
import parser as ps

short_name = 'tree_generator'

def count_vertex(res):
    c = 0
    for r in res:
        if r == res:
            c = 1
            break
        c += count_vertex(r)
    print res, c
    return c

def dict_tree(res):
    if isinstance(res, float) or isinstance(res, int) or isinstance(res, str):
        return {'type': 'const', 'value': res}
    if len(res) == 1:
        n = res[0]
        if n == res:
            return {'type': 'variable', 'value': str(res)}
        else:
            return dict_tree(n)
    if len(res) == 2:
        return { 'type': 'call', 'name': res[0],  'args': [dict_tree(r) for r in res[1]]}
    if len(res) % 2 == 1:
        return {'type': 'infix', 'name': res[1], 'args': [dict_tree(res[2 * k]) for k in range((len(res) + 1) / 2)]}
    raise ValueError('Incorrect list length: {}'.format(res))

def compile_alpha(d):
    if not d:
        return ''
    if d['type'] == 'infix':
        return d['name'].join(['(' + compile_alpha(arg) + ')' for arg in d['args']])
    elif d['type'] == 'call':
        return d['name'] + '(' + ','.join([compile_alpha(arg) for arg in d['args']]) + ')'
    elif d['type'] == 'const' or d['type'] == 'variable':
        return str(d['value'])

def is_const(node):
    if not 'value' in node:
        return False
    try:
        f = float(node['value'])
        return True
    except:
        return False

def mix_trees_(node1, node2, path1, path2, node_pairs, prob=0.2):
    if (path1, path2) in node_pairs or node1['type'] == 'const' or node2['type'] == 'const':
        return False
    node_pairs.add((path1, path2))
    if node1['name'] == node2['name'] and random.uniform() < prob:
        args_num = len(node1['args'])
        ind1, ind2 = random.randint(0,args_num), random.randint(0,args_num)
        if compile_alpha(node1['args'][ind1]) == compile_alpha(node2['args'][ind2]) or \
            is_const(node1['args'][ind1]) or is_const(node2['args'][ind2]):
            return False
        else:
            node1['args'][ind1] = node2['args'][ind2]
            return True
    else:
        for child1 in node1['args']:
            if mix_trees_(child1, node2, path1+str(id(child1)), path2, node_pairs):
                    return True
        for child2 in node2['args']:
            if mix_trees_(node1, child2, path1, path2+str(id(child2)), node_pairs):
                    return True

        return False

def mix_trees(node1, node2):
    for i in range(100):
        path1, path2 = str(id(node1)), str(id(node2))
        node_pairs = set({})
        if mix_trees_(node1, node2, path1, path2, node_pairs):
            return
    node1 = {
        'args': [copy.deepcopy(node1), node2],
        'name': '+',
        'type': 'infix',
    }

def get_subtree(node):
    if node['type'] == 'const':
        return node
    args_num = len(node['args'])
    while args_num != 0:
        ind = random.randint(0,args_num)
        res = node['args'][ind]
        if res['type'] == 'const':
            args_num = args_num - 1
            node['args'].remove(res)
        else:
            return res
    return res

def fix_unary_minus(alpha):
    alpha = '('+alpha+')'
    return alpha.replace('(-','(0-').replace('*-1','*(0-1)')

def origin_alpha_iterator():
    #return map(lambda alpha: alpha['code'], tops.top_sid_wo_capex())
    return map(lambda alpha: alpha['code'], tops.uncorr_top())

def get(alpha_from_stream = None):
    while True:
        if not alpha_from_stream:
            alphas = map(fix_unary_minus, random.choice(list(origin_alpha_iterator()), 10))
            for al1, al2 in itertools.product(alphas, alphas):
                if al1 != al2:
                    try:
                        node1, node2 = dict_tree(ps.parse(al1)), dict_tree(ps.parse(al2))
                        check = copy.deepcopy(node1)
                        mix_trees(node1, node2)
                        if compile_alpha(node1) != compile_alpha(check):
                            yield {
                            'code': compile_alpha(node1),
                            'params_info': params_info_list.params_info,
                            }
                    except Exception as e:
                        print 'OLOLo error:', e
                        print 'Alpha_1', al1
                        print 'Alpha_2', al2
                        import traceback
                        traceback.print_exc()
        else:
            fix_alpha = fix_unary_minus(alpha_from_stream)
            alphas = map(fix_unary_minus, random.choice(list(origin_alpha_iterator()), 10))
            for al in alphas:
                try:
                    node1, node2 = dict_tree(ps.parse(al)), dict_tree(ps.parse(fix_alpha))
                    check = copy.deepcopy(node1)
                    mix_trees(node1, node2)
                    if compile_alpha(node1) != compile_alpha(check):
                        yield {
                        'code': compile_alpha(node1),
                        'params_info': params_info_list.params_info,
                        }
                except Exception as e:
                    print 'OLOLo error:', e
                    print 'Alpha_from_stream', alpha_from_stream
                    print 'Alpha_2', al
                    import traceback
                    traceback.print_exc()