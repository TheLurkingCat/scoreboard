﻿# Scoreboard for NCTU OJ

## Requirements
- Python 3
- Webdriver (Default is [Chrome](http://chromedriver.chromium.org/downloads))
- A json file named token.json contains your cookie of api.oj.nctu.me

## Python package requirements
- selenium
- pandas
- matplotlib

## Usage
```bash=
    python scoreboard.py
```

## Settings
### You can edit settings in settings.ini

#### If set picture_filename to no, the scoreboard will display on screen
#### Not recommend for lagre dara, it may cause serious lag.
- picture_filename = scoreboard.png
#### If set debug to yes, chrome will not work in headless mode.
- debug = no
#### Seperate each problem id by space.
- problems = 819 820 822 823 825 826 829 830

## Known issues
- The picture size may larger than the table, I don't know how to let it fit properly.