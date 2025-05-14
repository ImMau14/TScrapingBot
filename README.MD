<div align="center">
<h1>TScrapingBot</h1>

Un bot de Telegram enfocado en el web scraping aplicado con la inteligencia artificial. El bot está potenciado por Gemini 2.0.
</div>

## Funcionalidades

* Puedes hablar con Gemini con `/ask <mensaje>`.
* Puedes buscar en un sitio web con `/search <url del sitio> <mensaje>`.
* Puedes saber el precio del dólar en bolívares con `/dolar` (principalmente, el bot fue hecho para esto, la verdad).

## Futuras Funcionalidades

* Poder escribir `/weather <lugar> <mensaje>` y recibir el clima, además de lo que pidas por el mensaje.
* Poder navegar por internet.
* Implementar la capacidad de Gemini para procesar imágenes.
* Poder procesar documentos y archivos de texto.
* Poder procesar videos.
* Implementar una base de datos para hacer que Gemini pueda recordar conversaciones pasadas.

## Cómo Usar

### Necesitarás
* Una API Key de [Gemini](https://ai.google.dev/).
* Una API Key de [Scrape.do](https://scrape.do/).
* Crear un bot con [@BotFather](https://t.me/BotFather) (en Telegram).

Lo demás varía dependiendo si lo desplegarás o lo usarás local.

Debes crear un archivo .env en la raíz del proyecto con las siguientes variables:
```env
TELEGRAM_TOKEN = <Token de Telegram>
GEMINI_TOKEN = <API de Gemini>
SCRAPEDO_TOKEN = <API key de Scrape.do>
BOT_NAME = <Nombre del bot sin @>
```

Para desplegar el bot en [Render](https://render.com/), debes añadir las variables anteriores, más las siguientes:
```env
HOSTING = true
HOST = 8080
WEBHOOK_URL = <La URL de despliegue, ej. https://mibot.onrender.com>
```