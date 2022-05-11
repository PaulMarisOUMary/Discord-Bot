# ! SHOULD BE REMOVED IN PRODUCTION
import os, json, asyncio

from database import DataSQL

def getCredentials():
    source_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(source_directory, "config", "database.json"), "r") as data: 
        return json.load(data)["server"]

async def main(host, port, user, password, database):
    data = DataSQL(host=host, port=port)
    await data.auth(user=user, password=password, database=database)

    #await data.insert(table="table_metrics", args={"command_name": "test", "command_count": 1, "command_type": "test"})

    #await data.update(table="table_prefix", variable="guild_prefix", value="!", condition="guild_id=332234497078853644")
    #await data.update(table="table_metrics", variable="command_count", value=2, condition='command_name="test"')
    await data.increment_value(table="table_metrics", target="command_count", value=-3, condition='command_name="test"')

    print("done")

dbCred = getCredentials()
asyncio.run(main(dbCred["host"], dbCred["port"], dbCred["user"], dbCred["password"], "discord_dev"))

# ! SHOULD BE REMOVED IN PRODUCTION