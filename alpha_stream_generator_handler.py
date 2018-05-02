from sending import Sending
import random
import time
import alpha_stream
import generators.tops
import top_getter
import generators.tree_generator
import generators.alpha_stream_generator
import sending
import logging
import db_handler
import sending_result
import config
import sys

logger = logging.getLogger(__name__)


class AlphaStreamGeneratorHandler(object):
    '''
    Queue where alphaStreams are waiting for feedback
    '''

    def __init__(self):
        self.streamList = []
        self.db = db_handler.DBHandler()


    def add_stream(self, streamID = None, sending = None):
        if (not streamID) and (not sending):
            tg = top_getter.TopGetter()
            sending_list = tg.get_top_list('top_gen')
            self.streamList.append(alpha_stream.AlphaStream(sending = sending_list[random.randint(0, len(sending_list)-1)]))
        elif not sending:
            self.streamList.append(alpha_stream.AlphaStream(streamID))
        else:
            self.streamList.append(alpha_stream.AlphaStream(sending = sending))


    def loop(self):
        i = 0
        while True:
            sys.setrecursionlimit(1000)
            time.sleep(config.stream_sleep_time / len(self.streamList))
            self.streamList[i].update()
            stream = self.streamList[i]
            while len(stream.sending_list) == 1:
                asg = generators.alpha_stream_generator.AlphaStreamGenerator(stream)
                alpha = asg.get()["alpha"]
                code = alpha['code']
                check_code = ''
                sys.setrecursionlimit(3000)
                while len(code) > config.max_alpha_length:
                    logger.info('Truncation...')
                    check_code = code
                    code = asg.truncateAlpha(code)
                    if check_code == code:
                        logger.info('There is no possible to truncate')
                        break
                if check_code == code:
                    continue
                alpha['code'] = code
                logger.info("new alpha in handler: {}".format(alpha))
                snd = sending.Sending(code = alpha["code"], params = alpha["params"])
                stream.add(snd)
                logger.info('StreamID:{}; added sendingID = {}, len of stream = 2'.format(stream.alphaStreamID, snd.sendingID))
                continue
            #snd = stream.sending_list[-1].get_result()
            #logger.debug('-1 SendingID: {}, result: {}'.format(stream.sending_list[-1].sendingID, stream.sending_list[-1].get_result().params))
            #logger.debug('-2 SendingID: {}, result: {}'.format(stream.sending_list[-2].sendingID, stream.sending_list[-2].get_result().params))
            snd = stream.sending_list[-1]
            snd_ = stream.sending_list[-2]
            if not snd.get_result().is_empty():
                if snd.get_result().adjusted_fitness() <= snd_.get_result().adjusted_fitness():
                    stream.remove_last()
                asg = generators.alpha_stream_generator.AlphaStreamGenerator(stream)
                alpha = asg.get()["alpha"]
                code = alpha['code']
                check_code = ''
                sys.setrecursionlimit(3000)
                while len(code) > config.max_alpha_length:
                    logger.info('Truncation...')
                    check_code = code
                    code = asg.truncateAlpha(code)
                    if check_code == code:
                        logger.info('There is no possible to truncate')
                        break
                if check_code != code:
                    alpha['code'] = code
                    snd = sending.Sending(code = alpha["code"], params = alpha["params"])
                    stream.add(snd)
                    logger.info('StreamID:{}; added sendingID = {}, len of stream = {}'.format(stream.alphaStreamID, snd.sendingID, len(stream.sending_list)))
            
            elif snd.get_status() not in [None, 'processing', 'done']:
                stream.remove_last()
                logger.info('Last alpha was not simulated, removing..')
            else:
                logger.info('StreamID:{}; last sendingID = {} has not result, len of stream = {}'.format(stream.alphaStreamID, snd.sendingID, len(stream.sending_list)))
            i = (i + 1) % len(self.streamList)
