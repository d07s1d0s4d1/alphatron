import sending_result
import sending
import db_handler

class AlphaStream(object):
    '''
    This is the seuqence of alphas.
    use self.sending_result_list to see the stream
    '''
    def __init__(self, alphaStreamID = None, sending = None):
        '''
        :param alphaStreamID: if presented, creates presentation of passed steramId
        :param sendingID: if presented, creates new alphaStrem (and creates presentation object), containing the sending
        :returns: presentation of alphaStreeamId object (that is new, if sendingId passed)
        '''
        self.db = db_handler.DBHandler()

        self.sending_list = []
        if not alphaStreamID:
            self.alphaStreamID = self.db.alpha_stream_create(sending.sendingID)
        else:
            self.alphaStreamID = alphaStreamID

        self.__update_sequence()

    def remove_last(self):
        '''
        :action: removes last added sending_id of the stream
        '''
        self.db.alpha_stream_remove_last(self.alphaStreamID)
        self.__update_sequence()

    def add(self, sending):
        '''
        :action: add new sending to the stream
        '''
        self.db.alpha_stream_add(self.alphaStreamID, sending.sendingID)
        self.__update_sequence()

    def update(self):
        self.__update_sequence()


    def __update_sequence(self):
        '''
        :action: updates the self.sending_result_list
        '''
        self.sending_list = map(sending.Sending, self.db.alpha_stream_get_sendingIDs(self.alphaStreamID))
