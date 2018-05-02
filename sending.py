import db_handler
import sending_result
import generators.params_info_list

class Sending(object):
    '''
    code and params of alpha, add sending to db in init
    '''

    def __init__(self, sendingID = None, code = None, params = {'delay': 0, 'decay': 7, 'univid': 'TOP2000', 'opneut': 'Subindustry'}, status = None):
        self.db = db_handler.DBHandler()
        self.__code = None
        self.__params = None
        self.__result = None
        self.__status = None

        if not sendingID:
            self.__code = code
            self.__params = params
            codeID = self.db.add_code(code)
            self.sendingID = self.db.add_sending(codeID, delay = params['delay'], decay = params['decay'], univid = params['univid'], opneut = params['opneut'])
        else:
            self.sendingID = sendingID
            self.__status = self.db.get_sending_status(sendingID)


    def get_result(self):
        if not self.__result:
            self.__result = sending_result.SendingResult(self.sendingID)
        return self.__result

    def get_params(self):
        if not self.__params:
            params_ = self.db.get_sending_params(self.sendingID)
            self.__code = params_['code']
            params_.pop('code')
            self.__params = params_
        return {
            'code': self.__code,
            'params': self.__params
        }

    def get_sending_id(self):
        return self.sendingID

    def update_status(self):
        self.__status = self.db.get_sending_status(self.sendingID)

    def get_status(self):
        self.update_status()
        return self.__status
