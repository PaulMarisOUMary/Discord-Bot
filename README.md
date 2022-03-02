![GitHub is maintained](https://img.shields.io/maintenance/yes/2022?color=success)
![GitHub last commit](https://img.shields.io/github/last-commit/PaulMarisOUMary/Algosup-Discord?color=informational)
![GitHub last release](https://img.shields.io/github/v/release/PaulMarisOUMary/Algosup-Discord?color=blueviolet)
  
# Algobot

## Table of content

- [About the project](#about-the-project)
	- [Built with](#built-with)
- [Getting started](#getting-started)
	- [Python prerequisites](#python-prerequisites)
	- [Discord developper configuration](#discord-developper-configuration)
	- [Configure the bot](#configure-the-bot)
- [SQL](#sql)
	- [SQL tables structure](#sql-tables-structure)
- [Available commands](#available-commands)
- [Images](#images)
## About the project

This discord bot was made for Algosup in 2020. It has a lot of features such translator, events manager, utils, and more. Made by student(s) for students.

### Built with

- [Python](https://python.org/) >= 3.8
- [discord.py](https://discordpy.readthedocs.io) >= 2.0.0a
- SQL
	- MariaDB (or MySQL)

## Getting started

### Python Prerequisites

Install python packages with:
- pip
```bash
$ pip install -r requirements.txt
```

# Windows
$ python3 -m pip install -U .[voice]
# Linux / MacOS
$ python3 -m pip install -U ".[voice]"

### Discord developper configuration
1. Create a application on [Discord Developpers](https://discord.com/developers/applications)

2. Enable the bot status in [Discord Developpers/applications/YOUR_APP_ID/bot](https://discord.com/developers/applications/YOUR_APP_ID/bot)

3. Please make sure you have activated each `Privileged Gateway Intents` in [Discord Developpers/applications/YOUR_APP_ID/bot #Privileged Gateway Intents](https://discord.com/developers/applications) for your application.

4. Copy the token bot from [Discord Developpers/applications/YOUR_APP_ID/bot #Token](https://discord.com/developers/applications/YOUR_APP_ID/bot)

### Configure the bot

1. Paste your dicord bot token in the `"token"` field inside `auth/auth.json`.

2. Configure the prefix in the `config\bot.json`.

3. If you're using the database, you need to configure the `config\database.json` file.
:warning: If you're NOT using any database, delete the following cogs: `fridaycake`, `me` & `birthday`.

## SQL

### SQL tables structure
- `table_birthday`
```sql
CREATE TABLE IF NOT EXISTS `table_birthday`
(
    `user_id`           BIGINT unsigned NOT NULL,
    `user_birth`        DATE NOT NULL,
UNIQUE(`user_id`)
)
ENGINE = InnoDB,
CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;
```

- `table_fridaycake`
```sql
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
```

- `table_me`
```sql
CREATE TABLE IF NOT EXISTS `table_me`
(
    `user_id`           BIGINT unsigned NOT NULL,
    `user_me`           varchar(1024),
UNIQUE(`user_id`)
)
ENGINE = InnoDB,
CHARACTER SET utf8mb4,
COLLATE utf8mb4_unicode_ci;
```

## Available commands

<details>

<summary>Show available commands</summary>

([smth,smthelse] are aliases)

  

- ADMIN:

```c#

?deletechannel {name}

["delc"]

  

?killloop {cog}

["kill"]

  

?reload {cog}

["rel"]

  

?reloadall

["rell", "relall"]

  

?reloadviews

["rmod", "rview", "rviews"]

```

  

- BASIC:

```c#

?help

["h", "?", "commands"]

  

?ping

[]

```



- BIRTHDAY:

```c#

?birthday

["bd", "setbirthday", "setbirth", "birth"]

  

?showbirthday

['showbirth', 'sbd']

```

  

- FRIDAYCAKE:

```c#

?fridaycake

["fc"]

  

?all

["a", "fa"]

  

?next

["n", "nc"]

  

?when

["w", "fw"]

```



- INFO:

```c#

?emojilist

["ce", "el"]

?lookup {user}

["lk"]

?profilepicture

["pp"]

?stat

['status','graph','gs','sg']

```


- ME:

```c#

?description

["me"]

  

?showdescription

["sme", "showme"]

```

  

- PRIVATETEXTUAL:

```c#

?createprivate

["create", "+"]

  

?deleteprivate

["delete", "-"]

  

?renameprivate

["rename", "_"]

  

?addprivate

["add", ">"]

```

  

- SPOTIFY:

```c#

?spotify {user}

["sp", "sy", "spy", "spot"]

```

  

- USEFULL:

```c#

?strawpoll

["stp", "straw", "sondage"]

```

</details>

  

## Images:

<details>

<summary>Show images/icons</summary>

  

## Algosup (students)

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_base.png?raw=true)

  

## ALPHA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_alpha.png?raw=true)

- Promotion Alpha 2020-2021 : `Aurélien`  `Brendon`  `Clément`  `Clémentine`  `Eloi` ~~`Eric`~~ `Florent`  `Ivan` ~~`Jules`~~ `Karine`  `Laura-Lee`  `Laurent`  `Louis`  `Martin`  `Max`  `Paul` ~~`Robin`~~ `Romain`  `Salahedine` ~~`Steevy`~~ `Théo`

## BETA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_beta.png?raw=true)

- Promotion Beta 2021-2022 : `Alexandre`  `Antonin`  `Arthur`  `David`  `Elise`  `Gaël`  `Guillaume`  `Léo`  `Mathieu`  `Maxime`  `Nicolas`  `Paul`  `Pierre`  `Quentin`  `Robin`  `Théo`  `Thomas`

## GAMMA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_gamma.png?raw=true)

- Promotion Gamma 2022-2023 :

## DELTA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_delta.png?raw=true)

- Promotion Delta 2023-2024 :

## EPSILON

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_epsilon.png?raw=true)

- Promotion Epsilon 2024-2025 :

## ZETA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_zeta.png?raw=true)

- Promotion Zeta 2025-2026 :

## ETA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_eta.png?raw=true)

- Promotion Eta 2026-2027 :

## THETA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_theta.png?raw=true)

- Promotion Theta 2027-2028 :

## IOTA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_Iota.png?raw=true)

- Promotion Iota 2028-2029 :

## KAPPA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_kappa.png?raw=true)

- Promotion Kappa 2029-2030 :

## LAMBDA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_lambda.png?raw=true)

- Promotion Lambda 2030-2031 :

## MU

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_mu.png?raw=true)

- Promotion Mu 2031-2032 :

## NU

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_nu.png?raw=true)

- Promotion Nu 2032-2033 :

## XI

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_xi.png?raw=true)

- Promotion Xi 2033-2034 :

## OMICRON

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_omicron.png?raw=true)

- Promotion Omicron 2034-2035 :

## PI

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_pi.png?raw=true)

- Promotion Pi 2035-2036 :

## RHO

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_rho.png?raw=true)

- Promotion Rho 2036-2037 :

## SIGMA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_sigma.png?raw=true)

- Promotion Sigma 2037-2038 :

## TAU

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_tau.png?raw=true)

- Promotion Tau 2038-2039 :

## UPSILON

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_upsilon.png?raw=true)

- Promotion Upsilon 2039-2040 :

## PHI

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_phi.png?raw=true)

- Promotion Phi 2040-2041 :

## CHI

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_chi.png?raw=true)

- Promotion Chi 2041-2042 :

## PSI

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_psi.png?raw=true)

- Promotion Psi 2042-2043 :

## OMEGA

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_omega.png?raw=true)

- Promotion Omega 2043-2044 :

## Algosup (sample)

![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup.png?raw=true)

## Discord bot logo (sample)

![](https://github.com/PaulMarisOUMary/Algosup-Discord/blob/main/images/bot_logo.png?raw=true)

</details>

  

<h5>Contributors :</h5>

<a  href="https://github.com/PaulMarisOUMary/Algosup-Discord/graphs/contributors">

<img  width="75px"  src="https://contrib.rocks/image?repo=PaulMarisOUMary/Algosup-Discord" />

</a>
