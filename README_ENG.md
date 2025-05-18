<div align="center">
<h1>TScrapingBot</h1>

A Telegram bot focused on web scraping applied with artificial intelligence. The bot is powered by Gemini 2.0.

Click here to use it on Telegram: TScrapingBot (https://t.me/TScrapingBot)

*[Readme en Español](./README.MD)*
</div>

## Features

* You can talk to Gemini with `/ask <message>`.
* You can search a website with `/search <website url> <message>`.
* You can find out the price of the dollar in bolivars with `/dolar` (mainly, the bot was made for this, to be honest).
* Being able to discuss various topics in separate threads within different chats.
* Being able to discuss topics with Gemini with the ability to remember messages.
* Being able to reset the topics per chat with /reset.

## Future Features

* Being able to write `/weather <place> <message>` and receive the weather, in addition to what you ask for in the message.
* Being able to write `/lang command` to configure the language output.
* Better control with the /reset command for operations such as resetting the history in all existing chats.
* Being able to browse the internet.
* Implement Gemini's ability to process images.
* Being able to process documents and text files.
* Being able to process videos.

## Data and Privacy

### Data and Experience

* For the history and language of Gemini's responses to function correctly, the user needs to be registered in the database to obtain their preferred language before generating the response.

* To maintain threads in different chats, it is necessary to save the chat ID, as TScrapingBot uses it to recognize where it is responding.

* In order to remember past conversations, the input and output messages of the bot are saved.

* The user is registered once they execute `/ask` or `/search`.

### Integrity

The data will not be shared with third parties or used for any purpose other than the development and functionalities of TScrapingBot.

## How to Deploy

### You will need
* A Gemini [Gemini](https://ai.google.dev/) API Key.
* A [Scrape.do](https://scrape.do/) API Key.
* Create a bot with [@BotFather](https://t.me/BotFather) (on Telegram).
* A [Supabase](https://supabase.com/) API URL and token.
  - The database must have this structure:
  An image will go here, but I haven't put it yet...

The rest varies depending on whether you will deploy it or use it locally.

You must create a .env file in the project root with the following variables:
```
TELEGRAM_TOKEN = <Telegram Token>
GEMINI_TOKEN = <Gemini API>
SCRAPEDO_TOKEN = <Scrape.do API key>
BOT_NAME = <Bot name without @>
SUPABASE_URL = <Supabase API URL>
SUPABASE_KEY = <Supabase Token>
```

To deploy the bot on [Render](https://render.com/), you must add the previous variables, plus the following:
```
HOSTING = true
HOST = 8080
WEBHOOK_URL = <The deployment URL, e.g. https://mybot.onrender.com>
```