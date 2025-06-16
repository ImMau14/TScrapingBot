# 🕸 TScrapingBot 1.4.0

![Python](https://img.shields.io/badge/Python-001f2d?style=for-the-badge\&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-041453?style=for-the-badge\&logo=telegram\&logoColor=046dac)
![Flask](https://img.shields.io/badge/Flask-010101?style=for-the-badge\&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini-00436b?style=for-the-badge\&logo=googlegemini\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-27273e?style=for-the-badge\&logo=postgresql)
![Requests](https://img.shields.io/badge/Requests-white?style=for-the-badge\&logo=python\&logoColor=black)
![Beautiful Soup](https://img.shields.io/badge/Beautiful%20Soup-black?style=for-the-badge\&logo=python\&logoColor=white)

A Telegram bot for web scraping enhanced with artificial intelligence. Click here to use it on Telegram: [@TScrapingBot](https://t.me/TScrapingBot)

*[README en Español](./README.MD)*

## 🌟 Features

### ✅ Current

* Text responses powered by Gemini 2.0.
* Image analysis.
* URL content fetching and parsing.
* Memory in chats (only for `/ask` and `/search` commands).
* Retrieve the USD to VES exchange rate.

### 🔮 Upcoming

* Image generation.
* Voice-based conversation.
* Group chats.
* Processing of text documents and video files.
* Weather fetching.
* Navigate GitHub repositories.

## 📜 Commands

|          Command         |                    Action                   |
| :----------------------: | :-----------------------------------------: |
|         `/start`         |            Initialization command           |
|          `/ping`         |          Check if the bot is alive          |
|          `/help`         |           Show available commands           |
|         `/dolar`         |       Show current dollar value in VES      |
|      `/ask <prompt>`     |            Ask Gemini a question            |
| `/search <url> <prompt>` | Search within a URL and ask Gemini about it |

## 🚀 Deployment

### ⚙️ Requirements

* Python 3.11.* (or later).
* API key from [Gemini 2.0](https://ai.google.dev/).
* A bot token from [@BotFather](https://t.me/BotFather).
* Token from [Scrape.do](https://scrape.do/).
* Database, token and URL from [Supabase](https://supabase.com).

### 🗃️ Database

The required structure is shown in the following diagram (SQL code in [schema.sql](data/schema.sql)):

![Supabase Diagram](https://files.catbox.moe/a1xva7.png)

### 🔐 Environment Variables

#### 🧱 Basic

|     Variable     |          Value          |
| :--------------: | :---------------------: |
|  `GEMINI_TOKEN`  |    Your Gemini token    |
| `SCRAPEDO_TOKEN` |   Your Scrape.do token  |
|  `SUPABASE_KEY`  |    Your Supabase key    |
|  `SUPABASE_URL`  |    Your Supabase URL    |
| `TELEGRAM_TOKEN` | Your Telegram bot token |

#### 🛠️ Production Only

|    Variable   |   Value  |
| :-----------: | :------: |
|   `HOSTING`   |  `true`  |
| `WEBHOOK_URL` | Host URL |

### 📦 Installation

**These steps assume the database is already set up.**

1. Clone the repo and navigate into it:

```bash
git clone https://github.com/ImMau14/TScrapingBot
cd TScrapingBot
```

2. Start a virtual environment and install dependencies:

```bash
# On Linux/macOS
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

```bash
# On Windows
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

3. Copy and configure environment variables:

```bash
cp .env.template .env
nano .env # Or use your preferred text editor.
```

4. Run the bot:

```bash
# On Linux/macOS
python3 main.py
```

```bash
# On Windows
python main.py
```

## 🗂 Structure

```
TScrapingBot/
├── data/
│   ├── gemini_config.json    # Gemini mode configurations
│   └── messages.json         # Bot messages
├── modules/
│   ├── database.py           # Database functions
│   ├── dolar_scraper.py      # Dollar scraper function
│   ├── gemini.py             # Gemini handler class
│   ├── page_scraper.py       # Web scraping function
│   └── utils.py              # Utility functions
├── main.py                   # Main bot file
├── requirements.txt          # Dependencies
├── .env.template             # Environment variables template
├── .gitignore                # Git ignore
├── README_ENG.md             # English README
├── README.MD                 # Spanish README
└── LICENSE                   # MIT License
```

## ☁️ Deployed On

* Host: [Render](https://render.com).
* Database: [Supabase](https://supabase.com).

## 📜 Licence

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
