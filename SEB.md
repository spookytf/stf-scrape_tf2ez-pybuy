# Installation Guide for `Sebastian`
<sub>Author: Yours Truly, <i>Jason McElhenney.</i></sub>

**OPERATING SYSTEM**: `Microsoft Windows 10`  
**BROWSER**: `Google Chrome` 

> Alright buddy. This isn't going to be the easiest thing in the world, I'll be straight up with ya. I tried to make it easy 
> by building an executable, but it was eating time. The script is tested working on two `Windows 10` targets as of now,
> _(those being the PCs of [@zudsniper](https://github.com/zudsniper) and [@Osc44r](https://github.com/Osc44r))_ so it's 
> _very, very unlikely_ that the script **WON'T** run on your hardware. 
> 
> **Keep that in mind as you read this guide.**   
> <sub>_I'm not going to be held responsible for any damage done to your
> hardware, software, or sanity._ (I didn't even right that... `GitHub Copilot` did. But... true.)</sub>

---

## `STEP 1` CLONE THE REPOSITORY TO YOUR COMPUTER
Starting simple. First, read [this entire guide](https://gist.github.com/zudsniper/220b638ea7b60160979e283b1f91b064) that I wrote for your employees while to make onboarding them easier.  
This document goes over...
1. Downloading and configuring `Git Bash`, as well as the `git` command line tool.
> I'll cut you some slack on this one. [Go here.](https://git-scm.com/downloads) Downlaod `Git for Windows` and run the installer. Follow installer steps.  If you think of it, uncheck `Git GUI` from automatically installing as it is a terrible program, but ultimately harmless.
> ### Got it? _Good._
2. Downloading `gh`, the `GitHub CLI` tool that goes along with `git` and `git bash`.
> This isn't... _that_ difficult on Windows. [Go here.](https://cli.github.com/) Download the installer and run it. Follow the installer steps.
3. The concepts and principles of collaborating effectively and carefully using version contr- I can tell you're already nodding off. Fine. Don't read the rest.
4. The basics of `Markdown` and how to use it to write documentation. Yeah, no idea why I finished this list but here it is.

---

***ANYWAY***, back on track. Once you've got `git` and `gh` installed, open `git bash` AS **ADMINISTATOR** (right click the icon and select `Run as Administrator`) and follow along.

```sh
# first we need to log you into your GitHub account.  
$ gh auth login
# follow the steps that follow. You'll want to hit "Enter" a fair few times until you get a code to paste into your browser. 
# Go to https://github.com/login/device and paste the code into the box.
# You'll be prompted to log into your GitHub account. Do so.
# Then BOOM. We made it. Step 1. Almost.
# FIRST, figure out where you are. In life. In the world. In the universe. In the multiverse. In the multiverse of multiverses.
# after that, you'll want to navigate to the folder you want to clone the repository into.
$ cd /c/Users/sebastian/Desktop
# you made it. Somewhere. Now clone!
$ gh repo clone spookytf/stf-scrape_tf2ez-pybuy
# done. 
```
_I hope that one was easy!_  

---

## `STEP 2` INSTALLING THE DEPENDENCIES 
> wait no no no lol you need python first  
## `STEP 1.5` INSTALLING PYTHON  

[Download this.](https://www.python.org/downloads/) & run the installer. Version should be around `3.11.2`, but it probably is. Don't worry about that. Just install it.

... Ok just kidding, its not entirely that simple.  
> **NOTE**: Make sure to check the box that says `Add Python to PATH`. This will make it so you don't have to type `python` in front of every command you run.
> Also make _ABSOLUTELY_ sure you select the `install pip package manager` option. 

Cool ok so close... Kinda.  

# `STEP 2` INSTALLING THE DEPENDENCIES  
We made it. Now we need to install the dependencies.
Throw this into the same `git bash` instance which you have `cd`'d into the appropriate directory wherein you've just cloned the github repository containing the python files needed to run this script.  
*SIMPLE.*  
    
```sh
# install the dependencies
$ pip install -r requirements.txt
# done. 
```

Sleek. Clean. Easy. Might break.   
**_MIGHT._**
> If that works out, you're good to go. If it doesn't, you're going to have to do some troubleshooting. I'm not going to be able to help you with that. I'm sorry. I'm not a wizard. I'm just a guy who wrote a script.
> Oh wait, `Copilot` wrote that too. I do have to help you if you get stuck. FUCK

---

# `STEP 3` RUNNING THE SCRIPT  
Alrighty then buddy hold your horses, jeeeeee whizz.  
> We're almost there kind of. Probably.  

All we have to do is ~~run the script.~~ NO you IDIOT!! you thought you would get to run it _already?_ No no no no no no no no no.  
We have to configure it first.  

---

## `STEP 3.1` CONFIGURING THE SCRIPT
> Ask me. I'll give you the config files. Lucky bastard.  
> you need `.env` and `config.ini`


---

# `STEP 4` RUNNING THE SCRIPT  
> I'm not going to tell you how to run the script. You're a smart person. You can figure it out.  

---

```sh
$ python main.py
# if that gives you trouble, try this instead
$ python -m pipreqs.pipreqs main.py 
# Hopefully that is enough to get you moving and shaking. I pray to god it is.
```

## `STEP 5` TROUBLESHOOTING
> Obviously just complain if its not working. 
> I didn't need to tell you that one did I?

Ideally at this point when you run aforementioned command within `git bash` you should see a GUI window open up.
_(GUI refering to `Graphical User Interface`)_  
If you don't see a GUI window open up, you're going to have to troubleshoot.

![Gorgeous frontend work](https://i.imgur.com/AqlFXT0.png)  
_If everything has worked out, you should see something like this._  

---

## `STEP 5.1` EPILOGUE  
> Congratulations! You've made it through a fair bit of tribulation, and I'm sure it took a bit of speculation on your part, or even rumination. 
> All the while, I've been in the inner sanctem, making sure that you don't get too far ahead of yourself.
> I'm gonna pass the fuck out.  
> Goodnight Hollywood.  
> Goodnight.

---

## `STEP 5.2` EPILOGUE 2: ELECTRIC BOOGALOO
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> I'm not going to be held responsible for any damage done to your hardware, software, or sanity.
> WOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
