import aiomysql
import asyncio
import json
import os

class DataSQL():
    def __init__(self, host="127.0.0.1", port=3306, loop=None) -> None:
        self.loop, self.host, self.port = loop, host, port

    async def auth(self, user="root", password='', database="mysql") -> None:
        self.connector = await aiomysql.connect(host=self.host, port=self.port, user=user, password=password, db=database, loop=self.loop, autocommit=True)

    async def query(self, query) -> tuple:
        async with self.connector.cursor() as cursor:
            await cursor.execute(query)
            response = await cursor.fetchall() 
            return response

    def insert(self, table, args) -> str:
        query, variables, values, lenght = "INSERT INTO `"+ str(table) +"` (", '', '', len(args)
        for i, arg in enumerate(args):
            variable, value, case = arg[0], arg[1], i+1

            variables += "`"+ str(variable) +"`, " if case < lenght else "`"+ str(variable) +"`"
            
            if isinstance(value, (str)): value = "'"+value+"'"
            values += str(value) +", " if case < lenght else str(value)

        query += variables +") VALUES ("+ values +");"

        return query

    def update(self, table, variable, value, condition) -> str:
        if isinstance(value, (str)): value = "'"+value+"'"
        return "UPDATE "+ str(table) +" SET `"+ str(variable) +"` = "+ str(value) +" WHERE "+ str(condition) +";"

    def select(self, table, target, condition) -> str:
        return "SELECT "+ str(target) +" FROM "+ str(table) +" WHERE "+ str(condition) +";"

    def close(self) -> None:
        self.connector.close()

"""
CREATE TABLE IF NOT EXISTS `table_fridaycake`
(
    `user_isin`         BOOLEAN NOT NULL,
    `user_id`           BIGINT unsigned NOT NULL,
    `user_name`         varchar(32) NOT NULL,

UNIQUE(`user_id`)
)
ENGINE = InnoDB,
CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;
"""

"""
INSERT INTO `table_fridaycake` (`user_isin`, `user_id`, `user_name`) 
VALUES (TRUE, 265148938091233293, 'Paul Maris');
"""


def getCredentials():
    source_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(source_directory, "auth", "auth.json"), "r") as data: 
        return json.load(data)["database"]

async def main(host, port, user, password, database):
    data = DataSQL(host=host, port=port, loop=asyncio.get_event_loop())

    await data.auth(user=user, password=password, database=database)

dbCred = getCredentials()
asyncio.run(main(dbCred["host"], dbCred["port"], dbCred["user"], dbCred["password"], "algosup_discord"))