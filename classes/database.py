import aiomysql
import asyncio

from datetime import datetime, date

class DataSQL():
    def __init__(self, host:str = "127.0.0.1", port:int = 3306, loop:asyncio.AbstractEventLoop = None) -> None:
        self.loop, self.host, self.port, self.connector = loop, host, port, None

    async def auth(self, user:str="root", password:str='', database:str="mysql", autocommit:bool = True) -> None:
        self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit = user, password, database, autocommit
        self.connector = await aiomysql.connect(
            host=self.host, 
            port=self.port, 
            user=user, 
            password=password, 
            db=database, 
            loop=self.loop, 
            autocommit=autocommit
        )

    async def query(self, query:str) -> tuple:
        async with self.connector.cursor() as cursor:
            try:
                await cursor.execute(query)
                response = await cursor.fetchall()
                return response

            except aiomysql.OperationalError as e:
                if e.args[0] == 2013: #Lost connection to SQL server during query
                    await self.auth(self.__authUser, self.__authPassword, self.__authDatabase, self.__authAutocommit)
                    return await self.query(query)
                return e            

            except Exception as e:
                return e
    
    async def select(self, table:str, target:str, condition:str = '', order:str = '') -> query:
        query = f"SELECT {target} FROM `{table}`"
        if condition: query += f" WHERE {condition}"
        if order: query += f" ORDER BY {order}"
        return await self.query(query + ';')

    async def count(self, table:str, what:str, condition:str = '') -> select:
        return await self.select(table, f"COUNT({what})", condition)

    async def lookup(self, table:str, target:str, what:str, which:str) -> select:
        return await self.select(table, target, f"{what} REGEXP '{which}'")
    
    async def exist(self, table:str, target:str, condition:str = '') -> bool:
        response = await self.count(table, target, condition)
        return response[0][0] > 0

    async def insert(self, table:str, args:dict) -> query:
        query, variables, values, lenght = f"INSERT INTO `{table}` (", '', '', len(args)
        for i, items in enumerate(args.items()):
            variable, value = items[0], items[1]
            
            variables += f"`{variable}`, " if i+1 < lenght else f"`{variable}`"

            kindFormat = self.__toKindFormat(value)
            if kindFormat: value = kindFormat
            
            values += f"{value}, " if i+1 < lenght else f"{value}"    

        query += f"{variables} ) VALUES ({values});"	 

        return await self.query(query)

    async def update(self, table:str, variable:str, value:any, condition:str) -> query:
        kindFormat = self.__toKindFormat(value)
        if kindFormat: value = kindFormat

        query = f"UPDATE {table} SET `{variable}` = {value}"
        if condition: query += f" WHERE {condition}"
        return await self.query(query + ';')

    def __toKindFormat(self, value:any = None) -> any:
        keeper = value
        if isinstance(value, (str)): value = f"'{value}'"
        elif isinstance(value, date): value = f"'{value.strftime('%Y-%m-%d')}'"
        elif isinstance(value, datetime): value = f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"

        if value != keeper: return value

    def close(self) -> None:
        self.connector.close()