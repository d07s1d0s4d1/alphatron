short_name = 'check101'

f = open('iter0alphas')

def get():
    for line in f.readlines():
        yield {
             'code':line.strip(),
             'params_info': {
                 'delay': ['0', '1'],
                'decay': ['7', '4', '1'],
                'univid': ['TOP2000', 'TOP200'],
                'opneut': ['Subindustry', 'Market']
            }
        }
        
get()