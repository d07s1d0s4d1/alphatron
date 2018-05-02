# -*- coding: utf-8 -*-
import db_handler
import websim
import correlation
import top_configs
from termcolor import colored
import logging
import config


logger = logging.getLogger(__name__)

class TopHandler(object):
    def __init__(self, accountID, top_config):
        self.accountID = accountID
        self.top_config = top_config
        self.db = db_handler.DBHandler()
        self.corr = correlation.Correlation(accountID)

        account = self.db.get_websim_account(accountID)
        self.ws = websim.WebSim(login = account[0], password = account[1])
        self.ws.authorise()

    def reset(self):
        logger.info('Dropping...')
        self.db.top_reset(self.top_config['top_table_name'])
        logger.info('Done')
        top = []
        used = set({})
        logger.info('Get good alphas...')
        good_alphas = list(self.db.iterate_over_good_alpha(min_fitness = self.top_config['min_fitness'], limit = self.top_config['max_top']))
        logger.info('Done')
        total_alphas = len(set(map(lambda x: x['sendingID'], good_alphas)))
        for i, alpha in enumerate(good_alphas):
            if alpha['sendingID'] in used:
                continue
            used.add(alpha['sendingID'])
            logger.info('Next alpha: {}'.format(alpha['code']))

            if self.try_to_add_to_top(alpha['sendingID'], top):
                top.append(alpha)

            logger.info('Status: {} of {} done; uinq: {} of {}; top size: {}'.format(i, len(good_alphas), len(used), total_alphas, len(top)))

    def check_top_candidate_for_fitness(self, sendingID):
        alpha = self.db.get_sending_result(sendingID)
        if alpha == None:
            logger.error('Empty result for alpha({}), excepted non-empty result for alpha'.format(str(alpha['sendingID'])))
            return False
        elif alpha['fitness']<self.top_config['min_fitness']:
            logger.info('Alpha is not added to the table: {}. Reason: Fitness is less than the minimal fitness.'.format(self.top_config['top_table_name']))
            return False
        return True
        
    def check_top_candidate_for_correlation(self, sendingID, top = None):
        if self.top_config['corr'] == 1:
            return True
        
        if not top:
            top = self.db.iterate_over_top_alpha(self.top_config['top_table_name'])
        for t in top:
            if self.corr.is_big_correlation(t['sendingID'], sendingID, 1 - self.top_config['corr']):
                logger.info('Alpha is not added to the table: {}. Reason: Is too correlated with {}'.format(self.top_config['top_table_name'], t['code'])) 
                return False
        return True

    def check_top_candidate_for_submission(self, sendingID):
        if not self.top_config['submission']:
            return True
        
        alphaID = self.db.sendingID_to_alphaID(sendingID)
        res = self.ws.check_submission(alphaID)
        
        if res['status']:
            return True
        elif self.top_config['top_table_name'] == 'top_for_generators' and \
            res['error'] == 'Cannot submit alpha : Correlation above 0.7 with existing alphas and performance not better by 10.0% or more':
            return True
        else:
            logger.info('Alpha is not added to the table: {}. Reason: submission response: {}.'.format(self.top_config['top_table_name'], res['error']))
            return False


    def try_to_add_to_top(self, sendingID, top = None):
        """
        :param sendingID: sendingID of alpha which is checking at the top 
        :param top: current top is passed to a function check_top_candidate_for_correlation, if top = None then it is taken from the database
        :action: function puts alpha in the top table, if it passes validation
        :returns: true if alpha was placed in the top, false otherwise
        """
        if not top:
            top = list(self.db.iterate_over_top_alpha(self.top_config['top_table_name']))


        if self.check_top_candidate_for_submission(sendingID) and \
            self.check_top_candidate_for_fitness(sendingID) and \
            self.check_top_candidate_for_correlation(sendingID, top):
            alpha = self.db.get_sending_result(sendingID)
            logger.critical('One more alpha is mined in top: {}!!!; Code:{}; Fitness: {}; Top size: {}'.format(self.top_config['top_table_name'], \
                alpha['code'], alpha['fitness'], len(top) + 1))
            self.db.top_insert(sendingID, self.top_config['top_table_name'])
            return True
        return False

    def split_top(self, sendingID):
        pass

class AllTopHandler(object):
    def __init__(self, accountID):
        self.accountID = accountID
        self.tops = [TopHandler(accountID,top_configs.get_top_config(top_config)) for top_config in top_configs.get_name_list_of_top_tables()]

    def try_to_add_to_all_tops(self, sendingID):
        for top in self.tops:
            top.try_to_add_to_top(sendingID)

            