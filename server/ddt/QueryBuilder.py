import logging


class QueryFactory:
    def __init__(self, table, sel_list, con_list, agg_list, agg_level, agg_cond, order_list):
        self.table = table
        self.sel_list = sel_list
        self.con_list = con_list
        self.agg_list = agg_list
        self.agg_level = agg_level
        self.agg_cond = agg_cond
        self.order_list = order_list

    def getQuery(self):
        sql = 'SELECT {} '.format(','.join(self.sel_list))
        # for agg in self.agg_list:

