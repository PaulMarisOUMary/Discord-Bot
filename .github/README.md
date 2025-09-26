<!-- https://shields.io/ -->
![GitHub is maintained](https://img.shields.io/maintenance/yes/2025?label=Maintained&color=success&logo=github)
![Deploy](https://img.shields.io/github/actions/workflow/status/PaulMarisOUMary/Discord-Bot/runner-update-and-restart-bot.yml?branch=main&label=Deploy&logo=github)
<!-- ![CodeQL](https://img.shields.io/github/actions/workflow/status/PaulMarisOUMary/Discord-Bot/codeql-analysis.yml?branch=main&label=CodeQL&logo=github) -->

![Contributors](https://img.shields.io/github/contributors/PaulMarisOUMary/Discord-Bot?label=Contributors&color=informational&logo=github)
![GitHub last commit](https://img.shields.io/github/last-commit/PaulMarisOUMary/Discord-Bot?label=Last%20commit&color=informational&logo=github)
![GitHub last release](https://img.shields.io/github/v/release/PaulMarisOUMary/Discord-Bot?label=Release&color=blueviolet&logo=github)
![Github last prerelease](https://img.shields.io/github/v/release/PaulMarisOUMary/Discord-Bot?color=orange&include_prereleases&label=Pre-release&logo=github)

# Discord-Bot

A Discord bot that you can use as your own.<br>
Built with a robust structure, seamless error handling, and easy configuration. Configure and edit effortlessly for a personalized experience.

## About the project

This discord bot was made for an IT School in 2020. It has a lot of features including all the latest features from discord.py.

### Major features

- Administrative Tools
    - Custom prefix per guild
    - Invite tracker
- Developement & Tools
    - ANSI color support
    - Custom error handling
    - Dynamic structure (Does not require a reboot to apply changes in code & files)
    - Database support (SQL)
    - Docker support
    - Image processing
    - Logging
    - Multiple configs
    - Metrics about usage of the bot
    - Powerful, dev & debuging commands
    - Utility functions
    - Socket communication system
    - Views system
- Discord support
    - [AppCommands](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.AppCommand) (Slash-commands)
    - [Cogs](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Cog)/[GroupCogs](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=cogs#discord.ext.commands.GroupCog)
    - [Commands](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Group)
    - [ContextMenus](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.app_commands.ContextMenu) (Right-click commands)
    - [Custom-Modals](https://discordpy.readthedocs.io/en/latest/interactions/api.html#discord.ui.Modal) (Forms)
    - [Custom-Views](https://discordpy.readthedocs.io/en/latest/interactions/api.html?#discord.ui.View) (Buttons, Dropdown, ..)
    - [Groups](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.Group)
    - [HybridCommands](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html#discord.ext.commands.HybridCommand) (Slash-commands + Commands)
- User Interaction
    - Custom Help command
    - Dynamic Starboard
    - Language detector & Translation
    - Private vocal channel on demand (cog: privatevocal)
    - Reddit posts listener
- And more..

### Built with

- [Python 3](https://python.org/) >= 3.8
- [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/) == latest
- [discord.py](https://discordpy.readthedocs.io/en/stable/) == stable
- SQL
	- MariaDB (or MySQL)

> [!NOTE]
> More about requirements in the [requirements.txt](https://github.com/PaulMarisOUMary/Discord-Bot/blob/main/requirements.txt) file.

## Getting started

### Discord developer configuration

1. Create an application on [Discord Developpers](https://discord.com/developers/applications)

2. Enable the bot status in [Discord Developpers/applications/{YOUR_APP_ID}/bot](https://discord.com/developers/applications/{YOUR_APP_ID}/bot)

3. Please make sure you have enabled each needed `Privileged Gateway Intents` in [Discord Developpers/applications/{YOUR_APP_ID}/bot #Privileged Gateway Intents](https://discord.com/developers/applications{YOUR_APP_ID}/bot) for your application.

4. Copy the token bot from [Discord Developpers/applications/{YOUR_APP_ID}/bot #Token](https://discord.com/developers/applications/{YOUR_APP_ID}/bot)

> [!TIP]
> In URL replace `{YOUR_APP_ID}` with your own app/bot ID.

### Bot configuration

1. Paste your discord bot token after the `BOT_TOKEN=` inside `/config/.env`.

2. Configure the default prefix in the `/config/bot.json`.

## Run the bot

You can run the bot in **two ways**:

1. With Docker (recommended for production)
2. Manual setup (recommended for development)

### Docker

1. Make sure you have [Docker](https://docs.docker.com/get-docker/) installed on your machine.

2. Run the following command in the root of the project:
```bash
docker-compose --env-file ./config/.env up --build
```

3. Your bot is now running !

### Manual setup

A `Virtual Environment <https://docs.python.org/3/library/venv.html>`_ is recommended.

Install python packages with:
```bash
pip install -r requirements.txt
```

#### Configure the bot

1. If you are using a database, fill your database credentials in the `/config/.env` file.

2. Inside your SQL database, create the required tables, more about in the [SQL tables structure](#sql-tables-structure) section.

> [!IMPORTANT]
> If you are **NOT** using any/or a compatible database, check the [Acknowledgement section](#acknowledgement).

#### Run the bot

Run the following command in the root of the project:
```bash
python bot.py
```

If everything is configured correctly, you should see the bot coming online in your Discord server.

## Database

### Acknowledgement

> [!IMPORTANT]
> If you have not planned to use a SQL database:
> 1. set the `"use_database"` field to `false` in the `/config/bot.json` file.
> 2. in the folder `/cogs` you should remove the following files (which are using the database): `birthday.py`, `croissants.py`, `invite.py`, `me.py`, `metrics.py`, `starboard.py`.

To set up a SQL database such as MariaDB or any other SQL database, and host it on a Raspberry Pi or any other server, you need to follow these steps:

1. Install MariaDB or any other SQL database on the desired server. The installation process may vary depending on the operating system and which SQL database you have selected. You may also want to install a graphical user interface for your database, such as phpMyAdmin, which makes it easier to manage and configure your database.

2. Create a new user with password that the bot is going to use and grant the necessary permissions such as `SELECT`, `INSERT`, `UPDATE`, `DELETE`, and `SHOW DATABASES`.

3. If the database is on the same server, no additional configuration is usually required. However, if the database is hosted on a different server, you may need to configure network settings to allow access to the database server. Specifically, you might need to open port 3306, which is the default port for SQL databases, on the server where the database is hosted.

4. Create a new database. Add the tables listed in the [SQL tables structure](#sql-tables-structure) section. You can change the structure of the tables as you wish, but you will need to reconfigure some keys/values of the `/config/cogs.json`.

5. Fill the database settings for your bot in the `/config/.env`.

### SQL tables structure

You can find the SQL structure of the tables in `/database/structure.sql`.

> [!NOTE]
> These tables are required in the database if you have planned to use the bot as if provided

## Development

To add a new cog, place the Python file in the /cog folder.<br>
While the bot is running, you can dynamically register the cog using the `loadcog` command followed by the name of the file without the .py extension. If you make changes to the cog after registering it, simply use `rl` or `rel <cog_name>` to reload the cog without restarting the bot.

The following commands provide flexibility and efficiency during the development phase, allowing you to seamlessly update and test your bot without restarting it.

### Commands Overview:
| Command                     | Alias | Description                                              | Example                                       |
|-----------------------------|-------|----------------------------------------------------------|-----------------------------------------------|
| `?loadcog <cog_name>`       |       | Loads a cog from the /cogs directory.                    | `?loadcog basic`                              |
|                             |       |                                                          |                                               |
| `?unloadcog <cog_name>`     |       | Unloads a cog from the /cogs directory.                  | `?unloadcog basic`                            |
|                             |       |                                                          |                                               |
| `?reloadallcogs`            | `rell`| Reloads all cogs inside the /cogs directory.             | `?reloadallcogs`                              |
|                             |       |                                                          |                                               |
| `?reload <cog1> <cog2> ...` | `rel` | Reloads specified cogs from the /cogs directory.         | `?reload basic birthday`                      |
|                             |       |                                                          |                                               |
| `?reloadlatest <n_cogs>`    | `rl`  | Reloads the n latest edited cogs in the /cogs directory. | `?reloadlatest 3`                             |
|                             |       |                                                          |                                               |
| `?reloadviews`              | `rv`  | Reloads all registered views in the /views directory.    | `?reloadviews`                                |
|                             |       |                                                          |                                               |
| `?reloadconfig`             | `rc`  | Reloads all JSON config files inside the /config folder. | `?reloadconfig`                               |
|                             |       |                                                          |                                               |
| `?synctree <guild_id>`      | `st`  | Syncs applications commands with discord.                | `?synctree` or `?synctree 123456789012345678` |

Most of the time you will be using, `rl` for reloading the latest edited cogs and `rv` for reloading all registered views.<br>
These commands are essential for development, often used to quickly apply and test code changes, making the development process smooth and efficient.

## Workflows

### Update and restart discord bot

Github setup: 
- On Github.com go on [your project repository](https://github.com/{USER_NAME}/{PROJECT_NAME}/settings/actions/runners)
- Then click on `Settings` > `Actions` > `Runners` > `New self-hosted runner`.
- Then select the right `runner-image` related to your machine and the right `architecture`.
- Then follow the `Download` and the `Configure` instructions.

Server setup:
- If you want to start the self-runner on boot, you can follow [this guide](https://docs.github.com/en/actions/hosting-your-own-runners/configuring-the-self-hosted-runner-application-as-a-service).
:warning: The self-hosted runner should have the following permissions, `install apps` and `start/restart services`. (install the service as --user usernameWithPermissions)

Discord bot service:
This step is made for linux only.
- Create a service file in `/etc/systemd/system/your-service-name.service` with the following content:
```bash
[Unit]
Description=Discord bot startup service
After=multi-user.target

[Service]
Type=simple
Restart=no
User={usernameWithPermissions}
WorkingDirectory=/home/{username}/actions-runner/_work/Discord-Bot/Discord-Bot
ExecStart=python3 /home/{username}/actions-runner/_work/Discord-Bot/Discord-Bot/bot.py

[Install]
WantedBy=multi-user.target
```
> [!TIP]
> Replace `{username}` & `{usernameWithPermissions}` with your username and `Discord-Bot/Discord-Bot` with your project name.
> - Then enable the service with `systemctl enable your-service-name.service`   

<h5>Contributors :</h5>

<a  href="https://github.com/PaulMarisOUMary/Discord-Bot/graphs/contributors">
    <img  height="25px"  src="https://contrib.rocks/image?repo=PaulMarisOUMary/Discord-Bot" />
</a>