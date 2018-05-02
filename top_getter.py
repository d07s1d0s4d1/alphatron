import top_configs
import db_handler
import sending

class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

class TopGetter(Singleton, object):
    def __init__(self):
        self.db = db_handler.DBHandler()
        self.tops = {}

    def get_top_list(self, top_name):
        if top_name not in self.tops:
            top = []
            top_sendings = list(self.db.iterate_over_top_alpha(top_configs.top_configs[top_name]['top_table_name']))
            for sending_ in top_sendings:
                top.append(sending.Sending(sending_['sendingID']))
            self.tops[top_name] = top

        return self.tops[top_name]
