import psycopg2
import pandas as pd
import config
import time
import tabulate
from functools32 import lru_cache
import logging

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

class DBHandler(Singleton, object):
    def __init__(self):
        logger.info('DBHandler initialised: {}'.format(self))
        self.reconnect()

    def reconnect(self):
        logger.info('DB reconnect')
        self.conn = psycopg2.connect(
            dbname = config.db_dbname,
            user = config.db_user,
            port = config.db_port,
            host = config.db_host,
            password = config.db_password)

    def check_connect(function_to_decorate):
        def decorating_function(self, *args, **kwargs):

            try:
                cur = self.conn.cursor()
                cur.execute('SELECT 1')
            except Exception as e:
                logger.error('Connection was broken: {}'.format(str(e)))
                self.reconnect()

            return function_to_decorate(self, *args, **kwargs)

        return decorating_function

    @check_connect
    def add_code(self, code, params_info = '', comment = '', author = 'python'):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO code (code, comment, author, params_info) VALUES (%s, %s, %s, %s) RETURNING ID', (code, comment, author, params_info))
        codeID = cur.fetchone()
        self.conn.commit()
        return codeID

    @check_connect
    def add_sending(self, codeID, priority = 0, params = None, delay = '0', decay = '6', opneut = 'subindustry', backdays = '512', univid = 'TOP2000', optrunc = '0.04'):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO sending (codeID, params, delay, decay, opneut, backdays, univid, optrunc, priority) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING sending.ID',
                (codeID, params, delay, decay, opneut, backdays, univid, optrunc, priority))
        sendingID = cur.fetchone()
        self.conn.commit()
        return sendingID

    @check_connect
    def get_sending_to_exec(self, accountID):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID
            FROM
                sending JOIN code ON sending.codeID = code.ID
            WHERE
                sending.ID not in (SELECT sendingID FROM processing WHERE sendingID IS NOT NULL)
            order by sending.priority
            limit 1
        ''')
        res = cur.fetchone()
        if res == None:
            return None
        sendingID = res[0]
        cur.execute('''
            INSERT INTO
                 processing
             (sendingID, status, websim_accID)
            VALUES (%(sendingID)s, 'processing', %(accountID)s)
            RETURNING
                /*code.code,
                code.params_info,
                sending.params,
                sending.ID,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc*/
                sendingID
        ''', {'sendingID': sendingID, 'accountID': accountID})
        self.conn.commit()
        sendingID = cur.fetchone()[0]
        print sendingID
        cur.execute('''
            SELECT
                code.code,
                code.params_info,
                sending.params,
                sending.ID,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc
            FROM
                sending JOIN code ON sending.codeID = code.ID
            WHERE
                sending.ID = %s
            ORDER BY sending.priority
            LIMIT 1
        ''', (sendingID, ))
        sending = cur.fetchone()
        logger.debug('Sending: {}'.format(sending))
        return sending

    @check_connect
    def get_code_to_sending(self):
        '''
        http://stackoverflow.com/questions/6507475/job-queue-as-sql-table-with-multiple-consumers-postgresql
        '''
        cur = self.conn.cursor()
        cur.execute('''
            UPDATE
                code
            SET
                status = 'done'
            WHERE
                code.ID in (
                    SELECT
                        code.ID
                    FROM
                        code
                    WHERE
                        status = 'not_processed'
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED)
            RETURNING
                code.ID,
                code.code,
                code.params_info
        ''')
        code = cur.fetchone()
        return code

    @check_connect
    def get_websim_account(self, account_id):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                login,
                password,
                name,
                comment
            FROM
                websim_account
            where
                ID = %s
            limit 1
        ''', (account_id, ))
        account = cur.fetchone()
        if not account:
            raise ValueError('No account found')
        return account

    @check_connect
    def set_process_status(self, sendingID, accountID, status):
        assert status in ['done', 'processing', 'skipped'], 'Incorrect status'
        assert status in ['done', 'skipped'], 'Processing is set by sender.py'

        cur = self.conn.cursor()
        cur.execute('INSERT INTO processing (sendingID, status, websim_accID) VALUES (%s, %s, %s)', (sendingID, status, accountID))
        self.conn.commit()

    @check_connect
    def save_result(self, sendingID, res):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO grade (sendingID, error, result) VALUES (%s, %s, %s)', (sendingID, res['grade']['error'], res['grade']['result']))
        for year in res['simsummary']['result']:
            cur.execute('''INSERT INTO simsummary
                (sendingID, BookSize, DrawDown, Fitness, LongCount, Margin, PnL, Returns, Sharpe, ShortCount, TurnOver, Year, YearId)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (sendingID, year['BookSize'], year['DrawDown'], year['Fitness'], year['LongCount'],
                    year['Margin'], year['PnL'], year['Returns'], year['Sharpe'], year['ShortCount'],
                    year['TurnOver'], '0' if len(str(year['Year'])) > 4 else year['Year'], year['YearId']
                )
            )
        cur.execute('INSERT INTO response (sendingID, alphaID) VALUES (%s, %s)', (sendingID, res['alphaID']))
        self.conn.commit()

    @check_connect
    def reset_process(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM processing WHERE status = \'processing\'')
        self.conn.commit()

    @check_connect
    def reset_sending(self):
        cur = self.conn.cursor()
        cur.execute('''
            DELETE FROM sending
            WHERE sending.ID not in (SELECT sendingID FROM grade)
            ''')
        self.conn.commit()

    @check_connect
    def reset_non_prior_sending(self):
        cur = self.conn.cursor()
        cur.execute('''
            DELETE FROM sending
            WHERE
                sending.ID not in (SELECT sendingID FROM processing)
                AND sending.ID not in (SELECT sendingID FROM grade)
                AND sending.priority > 0
            ''')
        self.conn.commit()

    @check_connect
    def reset_code(self):
        cur = self.conn.cursor()
        cur.execute('''
            DELETE FROM code
            WHERE code.ID not in (SELECT codeID FROM sending)
            ''')
        self.conn.commit()

    @check_connect
    def top_reset(self,top_table_name):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM {top_table_name}'.format(top_table_name = top_table_name))
        self.conn.commit()

    @check_connect
    def top_insert(self, sendingID, top_table_name):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO {top_table_name} (sendingID) VALUES (%s)'.format(top_table_name = top_table_name), (sendingID, ))
        self.conn.commit()

    @check_connect
    def view_results(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                simsummary.fitness,
                simsummary.turnover,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
        ''')
        rows = list(cur.fetchall())
        df = pd.DataFrame.from_records(rows, columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'fitness', 'turnover', 'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority'])
        df['code.comment'] = map(lambda s: s[0:12], df['code.comment'].values)
        pd.options.display.width = 250
        pd.options.display.max_rows = 999
        pd.set_option('expand_frame_repr', False)
        pd.set_option('max_colwidth', 30)
        print df

    @check_connect
    def get_sending_result(self, sendingID):
        #Not all results were obtained!!!!!!!!!!!
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,                      
                code.comment,
                simsummary.fitness,
                simsummary.turnover,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
                AND sending.ID = %s
            LIMIT 1
        ''', (sendingID, ))
        rows = list(cur.fetchall())
        columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'fitness', 'turnover', 'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority']
        return dict(zip(columns, rows[0])) if len(rows) > 0 else None

    @check_connect
    def get_sending_params(self, sendingID):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                code.author,
                code.comment,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
            WHERE
                sending.ID = %s
            LIMIT 1
        ''', (sendingID, ))
        rows = list(cur.fetchall())
        columns = ['sendingID','code', 'params_info',
            'params', 'code.author', 'code.comment',
            'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority']
        return dict(zip(columns, rows[0])) if len(rows) > 0 else None

    @check_connect
    def view_top_results(self, top_table_name):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                DISTINCT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                simsummary.fitness,
                simsummary.turnover,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
                JOIN {top_table_name} ON sending.ID = {top_table_name}.sendingID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
            ORDER BY simsummary.fitness DESC
        '''.format(top_table_name = top_table_name))
        rows = list(cur.fetchall())
        df = pd.DataFrame.from_records(rows, columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'fitness', 'turnover', 'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority'])
        df['code.comment'] = map(lambda s: s[0:12], df['code.comment'].values)
        pd.options.display.width = 250
        pd.options.display.max_rows = 999
        pd.set_option('expand_frame_repr', False)
        pd.set_option('max_colwidth', 30)
        print df

    @check_connect
    def view_good_results(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                simsummary.fitness,
                simsummary.turnover,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
                AND grade.result != 'Inferior'
        ''')
        rows = list(cur.fetchall())
        df = pd.DataFrame.from_records(rows, columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'fitness', 'turnover', 'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority'])
        df['code.comment'] = map(lambda s: s[0:12], df['code.comment'].values)
        pd.options.display.width = 250
        pd.options.display.max_rows = 999
        pd.set_option('expand_frame_repr', False)
        pd.set_option('max_colwidth', 30)
        print df

    @check_connect
    def detailed(self, sendingID):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                simsummary.fitness,
                simsummary.turnover,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID = %s
        ''', (sendingID, ))
        rows = cur.fetchall()
        columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'fitness', 'turnover', 'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority']
        for row in rows:
            for column, value in zip(columns, row):
                print '{}: {}'.format(column, value)
            print '----'

    @check_connect
    def get_processing_status(self):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                count(*) FILTER (WHERE sending.ID not in (SELECT sendingID FROM processing)) AS not_processed,
                count(*) FILTER (WHERE sending.ID in (SELECT sendingID FROM processing WHERE status = 'processing')
                            AND sending.ID not in (SELECT sendingID FROM processing WHERE status = 'done')) AS processing,
                count(*) FILTER (WHERE sending.ID not in (SELECT sendingID FROM processing) AND sending.priority = 0) AS not_processed_top_priority
            FROM
                sending
        ''')
        not_processed, processing, not_processed_top_priority = list(cur.fetchall())[0]
        print 'Not processed:', not_processed
        print 'Not processed top prior:', not_processed_top_priority
        print 'Processing:', processing

    @check_connect
    def iterate_over_good_alpha(self, min_fitness = 0., limit = 500):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                DISTINCT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority,
                simsummary.BookSize,
                simsummary.DrawDown,
                simsummary.Fitness,
                simsummary.LongCount,
                simsummary.Margin,
                simsummary.PnL,
                simsummary.Returns,
                simsummary.Sharpe,
                simsummary.ShortCount,
                simsummary.TurnOver
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
                JOIN response ON sending.ID = response.sendingID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
                AND not simsummary.fitness is null
                AND simsummary.fitness >= %s
            order by simsummary.fitness desc
            limit %s
        ''', (min_fitness, limit))
        columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority', 'booksize', 'drawdown', 'fitness', 'longcount', 'margin', 'pnl', 'returns',
            'sharpe', 'shortcount', 'turnover']
        for row in cur.fetchall():
            alpha = dict({})
            for column, value in zip(columns, row):
                alpha[column] = value
            yield alpha

    @check_connect
    def iterate_over_top_alpha(self, top_table_name):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                DISTINCT
                sending.ID,
                code.code,
                code.params_info,
                sending.params,
                grade.result,
                grade.error,
                code.author,
                code.comment,
                sending.delay,
                sending.decay,
                sending.opneut,
                sending.backdays,
                sending.univid,
                sending.optrunc,
                sending.priority,
                simsummary.BookSize,
                simsummary.DrawDown,
                simsummary.Fitness,
                simsummary.LongCount,
                simsummary.Margin,
                simsummary.PnL,
                simsummary.Returns,
                simsummary.Sharpe,
                simsummary.ShortCount,
                simsummary.TurnOver
            FROM
                sending JOIN code ON sending.codeID = code.ID
                LEFT JOIN grade ON grade.sendingID = sending.ID
                LEFT JOIN simsummary ON simsummary.sendingID = sending.ID
                JOIN response ON sending.ID = response.sendingID
                JOIN {top_table_name} ON sending.ID = {top_table_name}.sendingID
            WHERE
                (simsummary.YearID = 'TOTAL' or simsummary.YearID is null)
                AND sending.ID in (select sendingID from processing where status = 'done')
                AND not simsummary.fitness is null
            order by simsummary.fitness desc
        '''.format(top_table_name = top_table_name))
        columns = ['sendingID','code', 'params_info',
            'params', 'grade.result', 'grade.error', 'code.author', 'code.comment',
            'delay', 'decay', 'opneut', 'backdays', 'univid', 'optrunc',
            'priority', 'booksize', 'drawdown', 'fitness', 'longcount', 'margin', 'pnl', 'returns',
            'sharpe', 'shortcount', 'turnover']
        for row in cur.fetchall():
            alpha = dict({})
            for column, value in zip(columns, row):
                alpha[column] = value
            yield alpha

    @check_connect
    def save_correlation(self, res):
        cur = self.conn.cursor()
        if len(res) == 1:
            return # here is nothing to be saved: we have only one alpha.
        def rows():
            for alphaID_1 in res:
                for alphaID_2 in res[alphaID_1]:
                    if alphaID_1 == alphaID_2:
                        continue
                    yield (alphaID_1, alphaID_2, res[alphaID_1][alphaID_2])

        args_str = ','.join(cur.mogrify("(%s,%s,%s)", x) for x in rows())
        if args_str == '':
            logger.error('WTF? args_str is empty. res: {}'.format(res))
            return
        cur.execute("INSERT INTO correlation (alphaID_1, alphaID_2, corr) VALUES " + args_str)
        self.conn.commit()

    @check_connect
    def get_correlation(self, alphaID_1, alphaID_2):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                corr
            FROM
                correlation
            where
                alphaID_1 = %s
                AND alphaID_2 = %s
        ''', (alphaID_1, alphaID_2 ))

        res = cur.fetchall()
        if not len(res):
            return None
        return res[0][0]

    @check_connect
    @lru_cache(maxsize = 500)
    def sendingID_to_alphaID(self, sendingID):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sendingID,
                alphaID
            FROM
                response
            where sendingID = %s
        ''', (sendingID, ))

        res = cur.fetchall()
        if not len(res):
            raise ValueError('alphaID is unknown. SendingID: {}'.format(sendingID))
        return res[-1][1]

    @check_connect
    def is_big_correlation_trianle(self, sendingID_1, sendingID_2, beta):
        '''
        return true if it is proved, that correlation is big,
        false if it is not proved (but may be high-correltaed)
        '''
        assert 0 < beta and beta < 1
        return False

        alphaID_1 = self.sendingID_to_alphaID(sendingID_1)
        alphaID_2 = self.sendingID_to_alphaID(sendingID_2)

        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                c1.alphaID_2,
                c1.corr,
                c2.corr
            FROM
                correlation as c1
                JOIN correlation as c2 ON c1.alphaID_2 = c2.alphaID_1
            where
                c1.alphaID_1 = %(a1)s
                AND c2.alphaID_2 = %(a2)s
                AND c1.corr >= 1 - %(beta)s / 2
                AND c2.corr >= 1 - %(beta)s / 2
        ''', ({'a1': alphaID_1, 'a2': alphaID_2, 'beta': beta}))

        res = cur.fetchall()
        return len(res) > 0

    @check_connect
    def alpha_stream_create (self, sendingID):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO alpha_streams (sendingID, index) VALUES (%s, %s) RETURNING streamID', (sendingID, 0))
        streamID = cur.fetchone()
        self.conn.commit()
        return streamID

    @check_connect
    def alpha_stream_add (self, streamID, sendingID):
        cur = self.conn.cursor()
        cur.execute('''
            INSERT INTO
                alpha_streams (streamID, sendingID, index)
            VALUES (%(streamID)s, %(sendingID)s, (SELECT max(index) + 1 FROM alpha_streams WHERE streamID = %(streamID)s))''',
            {'streamID': streamID, 'sendingID': sendingID})
        self.conn.commit()

    @check_connect
    def alpha_stream_remove_last (self, streamID):
        cur = self.conn.cursor()
        cur.execute('''
            DELETE FROM
                alpha_streams
            WHERE
                streamID = %(streamID)s AND
                index = (SELECT max(index) FROM alpha_streams WHERE streamID = %(streamID)s)
            ''', {'streamID': streamID})
        self.conn.commit()

    @check_connect
    def alpha_stream_get_sendingIDs (self, streamID):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                sendingID
            FROM alpha_streams
            WHERE streamID = %s
            ORDER BY index
            ''', (streamID, ))
        sendingIDs = cur.fetchall()

        return sendingIDs

    @check_connect
    def reset_code(self):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM code WHERE code.ID not in (SELECT codeID FROM sending)')
        self.conn.commit()

    @check_connect
    def reset(self):
        cur = self.conn.cursor()
        cur.execute('DROP TABLE submit')
        self.conn.commit()
        cur.execute('DROP TABLE very_failed_alpha_id')
        self.conn.commit()
        cur.execute('DROP TABLE failed_alpha_id')
        self.conn.commit()
        cur.execute('DROP TABLE alpha_streams')
        self.conn.commit()
        cur.execute('DROP TABLE top_for_generators')
        self.conn.commit()
        cur.execute('DROP TABLE top')
        self.conn.commit()
        cur.execute('DROP TABLE correlation')
        self.conn.commit()
        cur.execute('DROP TABLE response')
        self.conn.commit()
        cur.execute('DROP TABLE simsummary')
        self.conn.commit()
        cur.execute('DROP TABLE grade')
        self.conn.commit()
        cur.execute('DROP TABLE processing')
        self.conn.commit()
        #cur.execute('DROP TABLE websim_account')
        #self.conn.commit()
        cur.execute('DROP TABLE sending')
        self.conn.commit()
        cur.execute('DROP TABLE code')
        self.conn.commit()
        cur.execute('''CREATE TABLE code (code text NOT NULL, params_info text, comment text, author text, ID Serial NOT NULL UNIQUE, 
            timestamp timestamp with time zone default (now() at time zone 'msk'), status varchar(100) default 'not_processed')''')
        self.conn.commit()
        cur.execute('''CREATE TABLE sending (codeID integer references code(ID), params text, ID Serial NOT NULL UNIQUE, delay text, 
            decay text, opneut text, backdays text, univid text, optrunc text, priority integer, 
            timestamp timestamp with time zone default (now() at time zone 'msk'))''')
        self.conn.commit()
        #cur.execute('''CREATE TABLE websim_account (login varchar(100), password varchar(100), name varchar(100), comment text, ID Serial NOT NULL UNIQUE)''')
        #self.conn.commit()
        cur.execute('''CREATE TABLE processing (sendingID integer references sending(ID), 
            websim_accID integer references websim_account(ID), status varchar(100))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE grade (sendingID integer references sending(ID), error text, result varchar(100))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE simsummary (sendingID integer references sending(ID), BookSize real, 
            DrawDown real, Fitness real, LongCount real, Margin real, PnL real, Returns real, Sharpe real, 
            ShortCount real, TurnOver real, Year integer, YearID varchar(20))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE response (sendingID integer references sending(ID), alphaID varchar(1000))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE correlation (alphaID_1 varchar(500), alphaID_2 varchar(500), corr real)''')
        self.conn.commit()
        cur.execute('''CREATE TABLE top (sendingID integer references sending(ID))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE top_for_generators (sendingID integer references sending(ID))''')
        self.conn.commit()
        cur.execute('''CREATE TABLE alpha_streams (streamID Serial NOT NULL, sendingID integer, index integer)''')
        self.conn.commit()
        cur.execute('''CREATE TABLE failed_alpha_id (alphaID varchar(500) UNIQUE)''')
        self.conn.commit()
        cur.execute('''CREATE TABLE very_failed_alpha_id (alphaID varchar(500) UNIQUE)''')
        self.conn.commit()
        cur.execute('''CREATE TABLE submit (sendingID integer references sending(ID), status varchar(100), comment varchar(1000))''')
        self.conn.commit()


    @check_connect
    def save_failed_alpha_id(self, alphaID):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO failed_alpha_id (alphaID) VALUES (%s) ON CONFLICT DO NOTHING', (alphaID, ))
        self.conn.commit()

    @check_connect
    def save_very_failed_alpha_id(self, alphaID):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO very_failed_alpha_id (alphaID) VALUES (%s) ON CONFLICT DO NOTHING', (alphaID, ))
        self.conn.commit()
        
    @check_connect
    def get_token(self, account_id):
        cur = self.conn.cursor()
        cur.execute('''
            UPDATE is_free SET false FROM tokens
            WHERE account = %s AND is_valid = True
            LIMIT 1
            RETURNING uid, wssid
            ''', account_id)
        token = cur.fetchall()
        return token
    
    @check_connect
    def free_token(self, token):
        cur = self.conn.cursor()
        cur.execute('UPDATE is_free SET True WHERE uid = %s', token)
        self.conn.commit()

    @check_connect
    def get_sending_status(self, sendingID):
        cur = self.conn.cursor()
        cur.execute('SELECT status FROM processing WHERE sendingid = %s', (sendingID, ))
        res = cur.fetchall()
        res = [x[0] for x in res]
        if res == []:
            return None
        for st in res:
            if st != 'processing':
                return st
        return 'processing'

    @check_connect
    def set_submit_status(self, sendingID, accountID, status, comment = None):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO submit (sendingID, client_accID, status, comment) VALUES (%s, %s, %s, %s)', (sendingID, accountID, status, comment))
        self.conn.commit()

    @check_connect
    def get_unsubmit_top_alphas(self, top_table_name):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT 
                (sendingid)
            FROM 
                {top_table_name}
            WHERE
                sendingid not in (SELECT (sendingid) FROM submit WHERE status = 'true')
            '''.format(top_table_name = top_table_name))
        res = cur.fetchall()
        res = [x[0] for x in res]
        return res

    @check_connect
    def get_client_account(self, account_id):
        cur = self.conn.cursor()
        cur.execute('''
            SELECT
                login,
                password,
                name,
                comment
            FROM
                client_account
            where
                ID = %s
            limit 1
        ''', (account_id, ))
        account = cur.fetchone()
        if not account:
            raise ValueError('No account found')
        return account