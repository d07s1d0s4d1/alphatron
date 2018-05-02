import db_handler
import correlation

class SendingResult(object):
    def __init__(self, sendingID):
        self.db = db_handler.DBHandler()

        self.sendingID = sendingID
        self.params = self.db.get_sending_result(sendingID)

    def adjusted_fitness(self, alpha = 1, c = 0.75, a = 10):
        '''
        c: min level at which correlation affect on adjusted_fitness
        a: fitness will be reduced by a if correlation == 1
        alpha: ratio supplements fitness  
        '''

        '''
        cr = correlation.Correlation(1)
    	corr = cr.max_top_correlation(self.sendingID, 'top_gen')
        if ((corr == None) or (self.params['fitness'] == None)):
            raise TypeError('Fitness:{}; Correlation:{}'.format(self.params['fitness'], corr))
    	return self.params['fitness'] - alpha * max(1./(1 - corr + 1./a) - 1./(1 - c + 1./a), 0)
        '''
        return self.params['fitness']

    def is_empty(self):
    	if not self.params:
    	    return True
    	return False