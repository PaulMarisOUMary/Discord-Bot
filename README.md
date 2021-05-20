
![GitHub last commit](https://img.shields.io/github/last-commit/PaulMarisOUMary/Algosup-Discord)

# Algobot

# Setting up the bot

<details>
  <summary>Get started</summary>
  
  - Paste your token  BOT in `auth/token.dat`.
  - Please make sure you have activated the `Privileged Gateway Intents` in [Discord Developpers](https://discord.com/developers/applications) for your application.
	  - [x] PRESENCE INTENT
	  - [x] SERVER MEMBERS INTENT
  - Install with `pip` all dependencies :
	  - [x] `python3 -m pip install -U discord.py`
	  - [x] `python3 -m pip install -U DateTime`
	  - [x] `python3 -m pip install -U matplotlib`
	  - [x] `python3 -m pip install -U O365`
	  - [x] `python3 -m pip install -U Pillow`
	  - [x] `python3 -m pip install -U googletrans==4.0.0-rc1`
  - Delete `auth/client.dat`, `auth/secret.dat`, `auth/tenant_id.dat` & `cogs/schedule.py` if you don't use O365 services.
  - Edit line `10` on `bot.py` to change the bot prefix : `command_prefix=commands.when_mentioned_or("PREFIX_HERE")`.
  - If you want to use admin commands edit the line `7` on `cogs/admin.py`and paste your user ID (more informations [here](https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-))
  
</details>

# Available commands

<details>
  <summary>Show available commands</summary>

([smth,smthelse] are aliases)

- ADMIN:
```c#
?deletechannel {name}
["dc"]

?killloop {cog}
["kill"]

?reload {cog}
["rel"]

?reloadall
["rell", "relall"]
```

- BASIC:
```c#
?help
["h", "?", "commands"]
```

- FRIDAYCAKE:
```c#
?cake
["fc"]

?all
["a"]

?next
["n"]

?when
["w"]
```

- PRIVATETEXTUAL:
```c#
?addprivate
["create", "add", "+", ">"]

?delprivate
["delete", "del", "-", "<"]

?renprivate
["rename", "ren", "r", "_"]
```

- SCHEDULE
```c#
?currentcalendar
["cc", "ac"]

?nextcalendar
["nc"]

?weekcalendar
["wc"]
```

- SPOTIFY:
```c#
?spotify {user}
["sp", "sy", "spy", "spot"]
```

- USEFULL:
```c#
?emojilist
["ce", "el"]

?strawpoll
["stp", "straw", "sondage"]
```
</details>

# Images:
<details>
  <summary>Show images/icons</summary>

## Algosup (students)
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_base.png?raw=true)

## ALPHA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_alpha.png?raw=true)
- Promotion 2020-2021 : `Aurélien` `Brendon` `Clément` `Clémentine` `Eloi` ~~`Eric`~~ `Florent` `Ivan` `Jules` `Karine` `Laura-Lee` `Laurent` `Louis` `Martin` `Max` `Paul` ~~`Robin`~~ `Romain` `Salahedine` ~~`Steevy`~~ `Théo`
## BETA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_beta.png?raw=true)
- Promotion 2021-2022 : 
## GAMMA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_gamma.png?raw=true)
- Promotion 2022-2023 : 
## DELTA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_delta.png?raw=true)
- Promotion 2023-2024 : 
## EPSILON
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_epsilon.png?raw=true)
- Promotion 2024-2025 : 
## ZETA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_zeta.png?raw=true)
- Promotion 2025-2026 : 
## ETA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_eta.png?raw=true)
- Promotion 2026-2027 : 
## THETA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_theta.png?raw=true)
- Promotion 2027-2028 : 
## IOTA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_Iota.png?raw=true)
- Promotion 2028-2029 : 
## KAPPA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_kappa.png?raw=true)
- Promotion 2029-2030 : 
## LAMBDA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_lambda.png?raw=true)
- Promotion 2030-2031 : 
## MU
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_mu.png?raw=true)
- Promotion 2031-2032 : 
## NU
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_nu.png?raw=true)
- Promotion 2032-2033 : 
## XI
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_xi.png?raw=true)
- Promotion 2033-2034 : 
## OMICRON
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_omicron.png?raw=true)
- Promotion 2034-2035 : 
## PI
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_pi.png?raw=true)
- Promotion 2035-2036 : 
## RHO
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_rho.png?raw=true)
- Promotion 2036-2037 : 
## SIGMA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_sigma.png?raw=true)
- Promotion 2037-2038 : 
## TAU
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_tau.png?raw=true)
- Promotion 2038-2039 : 
## UPSILON
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_upsilon.png?raw=true)
- Promotion 2039-2040 : 
## PHI
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_phi.png?raw=true)
- Promotion 2040-2041 : 
## CHI
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_chi.png?raw=true)
- Promotion 2041-2042 : 
## PSI
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_psi.png?raw=true)
- Promotion 2042-2043 : 
## OMEGA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_omega.png?raw=true)
- Promotion 2043-2044 : 
## Algosup (sample)
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup.png?raw=true)
## Discord bot logo (sample)
![](https://github.com/PaulMarisOUMary/Algosup-Discord/blob/main/images/bot_logo.png?raw=true)
</details>
