![GitHub is maintained](https://img.shields.io/maintenance/yes/2022?color=success)
![GitHub last commit](https://img.shields.io/github/last-commit/PaulMarisOUMary/Algosup-Discord?color=informational)
![GitHub last release](https://img.shields.io/github/v/release/PaulMarisOUMary/Algosup-Discord?color=blueviolet)

# Algobot

# Setting up the bot

<details>
  <summary>Get started</summary>
  
  - Please make sure you have activated the `Privileged Gateway Intents` in [Discord Developpers](https://discord.com/developers/applications) for your application.
  - Paste your BOT token in `auth/token.dat`.
	  - [x] PRESENCE INTENT
	  - [x] SERVER MEMBERS INTENT
  - Install with `pip` all dependencies :
	  - [x] `python3 -m pip install -U matplotlib`
	  - [x] `python3 -m pip install -U O365`
	  - [x] `python3 -m pip install -U Pillow`
	  - [x] `python3 -m pip install -U googletrans==4.0.0-rc1`
	  - [x] `python3 -m pip install -U tzlocal==2.1`
	  - [x] And the 2.0.0a discord.py version with :
	  ```bash
	  $ git clone https://github.com/Rapptz/discord.py
	  $ cd discord.py
	  $ python3 -m pip install -U .[voice]```
  - (Optional) Edit line `10` in `bot.py` to change the bot prefix : `command_prefix=commands.when_mentioned_or("`*PREFIX_HERE*`")`.
  
</details>

# Available commands

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
- Promotion Alpha 2020-2021 : `Aurélien` `Brendon` `Clément` `Clémentine` `Eloi` ~~`Eric`~~ `Florent` `Ivan` ~~`Jules`~~ `Karine` `Laura-Lee` `Laurent` `Louis` `Martin` `Max` `Paul` ~~`Robin`~~ `Romain` `Salahedine` ~~`Steevy`~~ `Théo`
## BETA
![](https://github.com/WarriorMachine/Algosup-Discord/blob/main/images/algosup_beta.png?raw=true)
- Promotion Beta 2021-2022 : `Alexandre` `Antonin` `Arthure` `David` `Elise` `Gaël` `Guillaume` `Léo` `Mathieu` `Maxime` `Nicolas` `Paul` `Pierre` `Quentin` `Robin` `Théo` `Thomas`
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
<a href="https://github.com/PaulMarisOUMary/Algosup-Discord/graphs/contributors">
  <img width="75px" src="https://contrib.rocks/image?repo=PaulMarisOUMary/Algosup-Discord" />
</a>
