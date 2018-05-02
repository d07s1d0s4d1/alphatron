short_name = 'dmy'

def get():
    n = 0
    while True:
        yield {
            'code': 'OLO {}'.format(n),
            'params_info': {
                'delay': ['0', '1'],
                'decay': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],

            }
        }
        n += 1
