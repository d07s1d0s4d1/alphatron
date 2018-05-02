import requests
import json
import time
import config
import logging
import db_handler

logger = logging.getLogger(__name__)
db = db_handler.DBHandler()

class WebSim(object):
    '''
    Example:
    ws = websim.WebSim(login = 'gosha-bor@yandex.ru', password = '...')
    ws.authorise()
    ws.send_alpha('-returns')
    '''
    def __init__(self, login = None, password = None, UID = None, WSSID = None, account_id = None):
        self.login = login
        self.password = password
        self.UID = UID
        self.WSSID = WSSID
        self.account_id = account_id
        self.headers = {
            'Host': 'websim.worldquantchallenge.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'application/json',
            'Accept-Language':'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://websim.worldquantchallenge.com',
            'Referer': 'https://websim.worldquantchallenge.com/result?q=9190149',
            'Connection': 'keep-alive',
        }

    def send_alpha(self, code, delay = "0", decay = 10, opneut = 'subindustry', optrunc = 0.03, univid = 'TOP3000', backdays = 256):
        
        while True:
            cookies = {
                'django_language': 'en',
            #    'sessionid': 'p50gmiem9hykheowx9vqp0o2k15ls3gh',
            #    '_xsrf': '2|c1d41832|6d1377ea652ff73e906cd52084aa5255|1491915833',
            #    'UID': '62c3eb61a6be7531aec6a64aed6522cd2cae1047adaf3f1a86f462cefe7e101a',
            #    'WSSID':'"2|1:0|10:1491934431|5:WSSID|60:eDdwUE9sZUhDeDE4NjQ5V05FYkJUa3hCakovd3FlUkZTdnkxOVEwRlAzcz0=|19cb0748569c793dcc2bfbf5c155112d41c6f3e1f1f1b45ad3036efbd2341b2a"',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }        
            r = requests.post('https://websim.worldquantchallenge.com/simulate',
                headers = self.headers,
                cookies = cookies,
                data = {'args': json.dumps([{
                    'delay': delay,
                    'unitcheck': 'off',
                    'univid': univid,
                    'opcodetype': 'EXPRESSION',
                    'opassetclass': 'EQUITY',
                    'optrunc': optrunc,
                    'code': code,
                    'region': 'USA',
                    'opneut': opneut,
                    'tags': 'equity',
                    'decay': decay,
                    'DataViz': 0,
                    'backdays': backdays,
                    'simtime': 'Y5'
                }])}
            )
#                     'IntradayType': 'null',       
#            print r
#            print r.text
            logger.debug(r.text)
            try:
                job = json.loads(r.text)
            except ValueError as info:
                logger.debug('Send request failed. Reason: {}'.format(info))
                self.authorise()
                continue
                #return 'CANCEL'
            res = {
                u'status': False, 
                u'result': [None], 
                u'error': {u'all': u'You have reached the limit of concurrent simulations. Please wait for the previous simulation(s) to finish.'},
            }
            if job == res:
                logger.info('Waiting concurrent jobs..')
                time.sleep(config.websim_concurrent_sleeptime)
            else:
                break
        if not job['status']:
            return 'CANCEL'
        job_id = job['result'][0]
        logger.debug('Job id: {}'.format(job_id))

#        print 'sending all'
        r = requests.post('https://websim.worldquantchallenge.com/simulate/settings/all',
            headers = self.headers,
            cookies = cookies,
        )
#        print r
#        print r.text
        all_ = json.loads(r.text)

#        print 'details'
        r = requests.post('https://websim.worldquantchallenge.com/job/details/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
#        print r
        logger.info('Details: {}'.format(r.text))
        details = json.loads(r.text)

        logger.info('Processing...')
        job_start_time = time.time()
        while True:

            if job_start_time + config.websim_job_time < time.time():
                logger.info('Exceeded the waiting limit')
                r = requests.post('https://websim.worldquantchallenge.com/cancelsim',
                    headers = self.headers,
                    cookies = cookies,
                    data = {
                        'q': job_id,
                    },
                )
                return 'CANCEL'

            time.sleep(config.websim_send_sleeptime)

#            print 'progress'
            r = requests.post('https://websim.worldquantchallenge.com/job/progress/{}'.format(job_id),
                headers = self.headers,
                cookies = cookies,
            )
            logger.debug('Temporal result: {}'.format(r.text))
            if r.text == "\"DONE\"":
                break
            elif r.text == "\"ERROR\"":
                logger.critical('Got ERROR in process request')
                return 'CANCEL'
            elif r.text == "\"CANCEL\"":
                return 'CANCEL'
            else:
                try:
                    int(r.text)
                except ValueError as info:
                    logger.debug('Process response failed, alpha will be skipped')
                    self.authorise()
                    return 'CANCEL'

        logger.info('Processed')

#        print 'details after done'
        r = requests.post('https://websim.worldquantchallenge.com/job/details/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
#        print r
#        print r.text
        details2 = json.loads(r.text)

        alphaID = details2['result']['clientAlphaId']
        logger.info('alphaID: {}'.format(alphaID))

        r = requests.post('https://websim.worldquantchallenge.com/job/pnlchart/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
        pnl_chart = json.loads(r.text)

        r = requests.post('https://websim.worldquantchallenge.com/job/grade/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
        grade = json.loads(r.text)

        r = requests.post('https://websim.worldquantchallenge.com/job/simsummary/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
        simsummary = json.loads(r.text)

        r = requests.post('https://websim.worldquantchallenge.com/job/simsummary/{}'.format(job_id),
            headers = self.headers,
            cookies = cookies,
        )
        simsummary = json.loads(r.text)
        return {
            'alphaID': alphaID,
            'grade': grade,
            'pnl_chart': pnl_chart,
            'simsummary': simsummary,
        }

    def correlation(self, alphaIDs, type_):
        assert type_ in ['inner_corr', 'self_corr']

        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/correlation/start',
                headers = self.headers,
                cookies = cookies,
                data = {
                    'args': json.dumps({
                        'alpha_list': alphaIDs,
                        'corr_type': type_,
                    })
                }
            )
            #print r
            #print r.text
            logger.debug('Correlation job: {}'.format(r.text))

            try:
                job = json.loads(r.text)
            except ValueError as info:
                logger.debug('Correlation send request failed. Reason: {}'.format(info))
                self.authorise()
                continue
                #return None
            break

        if not job['status']:
            return None
    
        job_id = job['result']['RequestId']
        #print job_id
        
        res = None
        inProgress = True
        corr_start_time = time.time()
        while inProgress:

            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }

            if corr_start_time + config.websim_corr_progress_sleeptime * len(alphaIDs) * len(alphaIDs) / 2 < time.time():
                return None
            time.sleep(config.websim_corr_sleeptime)

         #   print 'progress'
            r = requests.post('https://websim.worldquantchallenge.com/correlation/result/{}'.format(job_id),
                headers = self.headers,
                cookies = cookies,
            )
            logger.info(r.text)
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Correlation response failed. Reason: {}'.format(info))
                self.authorise()
                continue
                #return None
            inProgress = res['result']['InProgress']


        response = json.loads(res['result']['response'])

        return response

    def authorise(self):
        logger.info('Authorisation')
        while True:
            cookies = {
                    }
            r = requests.post('https://websim.worldquantchallenge.com/login/process',
                headers = self.headers,
                cookies = cookies,
                data = {
                    'EmailAddress': self.login,
                    'Password': self.password,
                    'next':'/dashboard',
                    'g-recaptcha-response': ''
                }
            )
            logger.debug('Authorisation response: {}'.format(r.text))
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.critical('Authorisation response failed. Reason: {}'.format(info))
                time.sleep(600)
                continue
            if res['status']:
                break
            else:
                logger.critical('Authorisation error: {}'.format(res['error']))
                time.sleep(600)

        #print r
        #print r.text
        #print r.cookies
        cookies_ = r.cookies.get_dict(domain = '.worldquantchallenge.com')
        #print r.cookies
        #logger.debug('COOKIES: {}'.format(cookies_))
        self.UID = cookies_['UID']
        self.WSSID = cookies_['WSSID']


    def get_random(self):
        raise ValueError('Do not use websim random!')
        cookies = {
            'django_language': 'en',
            'UID': self.UID,
            'WSSID': self.WSSID,
        }
        r = requests.post('https://websim.worldquantchallenge.com/random',
            headers = self.headers,
            cookies = cookies,
            data = {
                'tags': 'equity',
            }
        )
        print r
        print r.text
        job = json.loads(r.text)
        if not job['status']:
            raise ValueError(job)
        return job['result']

    def check_alpha_id(self, alphaID):

        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/alphainfo',
                headers = self.headers,
                cookies = cookies,
                data = {'args': json.dumps({'alpha_list': [alphaID]})}
            )

            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Checking alpha id failed. Reason: {}'.format(info))
                self.authorise()
                continue
            break

        logger.info('Check alphaID: {}'.format(alphaID))
        logger.info(res['status'])

        return res['status']

    def check_submission(self, alphaID):
        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/submission/check',
                headers = self.headers,
                cookies = cookies,
                data = {
                    'args': json.dumps({
                        'alpha_list': [alphaID],
                    })
                }
            )
            logger.info(r.text)
            
            try:
                job = json.loads(r.text)
            except ValueError as info:
                logger.debug('Checking submission send request failed. Reason: {}'.format(info))
                self.authorise()
                continue
            break
        if not job['error']:
            job_id = job['result']['RequestId']
        else:
            return job
        
        inProgress = True

        while inProgress:    
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }

            r = requests.post('https://websim.worldquantchallenge.com/submission/result/{}'.format(job_id),
                headers = self.headers,
                cookies = cookies,
            )
            
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Checking submission response failed. Reason: {}'.format(info))
                self.authorise()
                continue

            if res['error'] != None:
                break

            logger.info(res)
            inProgress = res['result']['InProgress']
            time.sleep(3)
        
        return res

    def submit(self, alphaID):
        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/submission/start',
                headers = self.headers,
                cookies = cookies,
                data = {
                    'args': json.dumps({
                        'alpha_list': [alphaID],
                    })
                }
            )
            logger.info(r.text)
            
            try:
                job = json.loads(r.text)
            except ValueError as info:
                logger.debug('Checking submission send request failed. Reason: {}'.format(info))
                self.authorise()
                continue
            break

        job_id = job['result']['RequestId']
        
        inProgress = True

        while inProgress:    
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }

            r = requests.post('https://websim.worldquantchallenge.com/submission/result/{}'.format(job_id),
                headers = self.headers,
                cookies = cookies,
            )
            
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Submit response failed. Reason: {}'.format(info))
                self.authorise()
                continue

            if res['error'] != None:
                break

            logger.info(res)
            inProgress = res['result']['InProgress']
            time.sleep(3)
        
        return res

    def get_state(self):
        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/contest/userdata/challenge',
                headers = self.headers,
                cookies = cookies,
            )
            logger.info(r.text)
            
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Receiving state request failed. Reason: {}'.format(info))
                self.authorise()
                continue
            break

        return res

    def get_my_alphas_count(self):
        while True:
            cookies = {
                'django_language': 'en',
                'UID': self.UID,
                'WSSID': self.WSSID,
            }
            r = requests.post('https://websim.worldquantchallenge.com/dashboard/myalphas',
                headers = self.headers,
                cookies = cookies,
            )
            logger.info(r.text)
            
            try:
                res = json.loads(r.text)
            except ValueError as info:
                logger.debug('Receiving alphas count request failed. Reason: {}'.format(info))
                self.authorise()
                continue
            break

        return res
    #def  __del__(self):
        #db.free_token(self.UID)