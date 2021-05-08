# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import copy
import datetime
from twisted.enterprise import adbapi
import pymysql.cursors
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MysqlPipeline:
    def __init__(self):
        self.dbpool = adbapi.ConnectionPool(
            'pymysql',
            host='localhost',
            db='ProxyPool',
            user='root',
            passwd='liuhaiyang210',
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8',
            use_unicode=True
        )
        self.web_info = {}

    def process_item(self, item, spider):
        """Process each item process_item"""
        asynItem = copy.deepcopy(item)  # 解决插入数据混乱重复的bug，添加同步锁。
        query = self.dbpool.runInteraction(self.__insertdata, asynItem, spider)
        query.addErrback(self.handle_error)

        if asynItem['web'] in self.web_info:
            self.web_info[asynItem['web']]['ip_num'] = self.web_info[asynItem['web']]['ip_num'] + 1
            self.web_info[asynItem['web']]['valid_num'] = self.web_info[asynItem['web']]['valid_num'] + \
                                                      (1 if asynItem['valid'] else 0)
        else:
            self.web_info[asynItem['web']] = {
                'name': asynItem['web'],
                'time': datetime.datetime.now(),
                'ip_num': 1,
                'valid_num': 1 if asynItem['valid'] else 0
            }

    def __insertdata(self, tx, item, spider):
        """Insert data into the database"""

        tx.execute("select * from ip_table where `id` = %s", item['id'])
        result = tx.fetchone()
        if result:
            logger.info("已经存在" + str(result))
            if result['valid'] != item['valid']:
                tx.execute("update ip_table set `valid` = %s where `id` = %s", (item['valid'], item['id']))
        else:
            insert_sql = """
                    insert into ip_table(`id`, `host`, `port`, `web`, `type`, `anonymous`, `region`, `valid`) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """
            tx.execute(insert_sql, (
                        item['id'],
                        item['host'],
                        item['port'],
                        item['web'],
                        item['type'],
                        item['anonymous'],
                        item['region'],
                        item['valid'],
                    ))

    def handle_error(self, e):
        """Handle error"""
        logger.error(e)

    def close_spider(self, spider):
        """close_spider the connection pool"""
        self.dbpool.close()
        logger.info(self.web_info)
        data = []
        for web in self.web_info.keys():
            web_info = self.web_info.get(web)
            data.append(list(web_info.values()))
        df = pd.DataFrame(data=data, columns=['web', 'time', 'ip_num', 'valid_num'])
        today = datetime.datetime.now()
        df.to_csv('output/web_info_{}_{}_{}.csv'.format(today.year, today.month, today.day))

