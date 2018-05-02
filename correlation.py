# -*- coding: utf-8 -*-
import db_handler
import websim
import logging
import top_getter

logger = logging.getLogger(__name__)

class Correlation():
    def __init__(self, accountID):
        self.accountID = accountID
        self.db = db_handler.DBHandler()

        account = self.db.get_websim_account(accountID)
        self.ws = websim.WebSim(login = account[0], password = account[1])
        self.ws.authorise()

    def request_correlation(self, alphaID_1 = None, alphaID_2 = None, alphaIDs = None):
        logger.info('Request websim corr')
        if not alphaIDs:
            alphaIDs = [alphaID_1, alphaID_2]

        for alphaID in alphaIDs:
            if not self.ws.check_alpha_id(alphaID):
                self.db.save_very_failed_alpha_id(alphaID)

        res = self.ws.correlation(alphaIDs, type_ = 'inner_corr')
        logger.info('WebSim correlation result: {}'.format(res))
        if not res:
            res = {}
        if len(res.keys()) < len(alphaIDs):
            res_alphas = res.keys()
            alphaIDs = list(set(alphaIDs))
            for alpha_1 in alphaIDs:
                if alpha_1 not in res_alphas:
                    self.db.save_failed_alpha_id(alpha_1)
                    if alpha_1 not in res.keys():
                        res[alpha_1] = {}
                    for alpha_2 in alphaIDs:
                        if alpha_1 == alpha_2:
                            res[alpha_1][alpha_2] = 1.
                        else:
                            res[alpha_1][alpha_2] = 0.
                else:
                    for alpha_2 in alphaIDs:
                        if alpha_2 not in res_alphas:
                            res[alpha_1][alpha_2] = 0.
            self.db.save_correlation(res)
            logger.info('Fix correlation result: {}'.format(res))
        else:
            self.db.save_correlation(res)
        '''
        if res:
            self.db.save_correlation(res)
        else:
            logger.error('WebSim result is empty')
        '''

    def correlation(self, sendingID_1, sendingID_2, fast = True):
        """
        sendingID — int or string
        fast — skip websim requesiting if there is no saved value in db
        return: float number in [0, 1]
        """
        alphaID_1 = self.db.sendingID_to_alphaID(sendingID_1)
        alphaID_2 = self.db.sendingID_to_alphaID(sendingID_2)
        logger.info('AlphaIDs: {}, {}'.format(alphaID_1, alphaID_2))
        corr = self.db.get_correlation(alphaID_1, alphaID_2)
        if corr:
            return corr

        if fast:
            return None

        self.request_correlation(alphaID_1, alphaID_2)
        corr = self.db.get_correlation(alphaID_1, alphaID_2)
        return corr

    def calc_correlations(self, sendingIDs):
        alphaIDs = map(lambda sid: self.db.sendingID_to_alphaID(sid), sendingIDs)
        corr = self.db.get_correlation(alphaIDs[0], alphaIDs[1])
        if corr:
            return

        self.request_correlation(alphaIDs = alphaIDs)


    def correlation_many(self, sendingIDlist, batch_size = 10):
        """
        all pair-wise correlations will be computed
        """
        assert batch_size <= 10
        cl = set({})
        for i, sendingID in enumerate(sendingIDlist):
            cl.add(sendingID)
            if len(cl) == batch_size:
                self.calc_correlations(cl)
                cl = set({})

    def is_big_correlation(self, sendingID_1, sendingID_2, beta, use_triangle = True):
        if use_triangle:
            logger.info('Sending IDs: {}, {}'.format(sendingID_1, sendingID_2))
            c = self.correlation(sendingID_1, sendingID_2, fast = True)
            if c:
                logger.info('Corr from db: {}'.format(c))
                return c >= 1 - beta
            res = self.db.is_big_correlation_trianle(sendingID_1, sendingID_2, beta)
            if res:
                logger.info('Corr is estimated by triangle')
                return True

            c = self.correlation(sendingID_1, sendingID_2, fast = False)
            logger.info('Corr from websim: {}'.format(c))
            return not c or c >= 1 - beta
        else:
            c = self.correlation(sendingID_1, sendingID_2, fast = False)
            return not c or c >= 1 - beta

    def max_correlation(self, sendingID, sendingIDlist):
        list_corr = []
        for sendingID_ in sendingIDlist:
            list_corr.append(self.correlation(sendingID, sendingID_, fast = False))

        return max(list_corr)

    def max_top_correlation(self, sendingID, top_name):
        tg = top_getter.TopGetter()
        top = tg.get_top_list('top_gen')
        return self.max_correlation(sendingID, [sending.sendingID for sending in top])