import params_info_list

short_name = '101alpha_gen'

f = open('iter0alphas', 'r')

def get():
    for line in f.readlines():
        yield {
                 'code': line.strip(),
                 'params_info': params_info_list.params_info,
              }