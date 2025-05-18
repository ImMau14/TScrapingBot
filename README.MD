<div align="center">
<h1>TScrapingBot</h1>

Un bot de Telegram enfocado en el web scraping aplicado con la inteligencia artificial. El bot está potenciado por Gemini 2.0.

Clic aquí para usarlo en Telegram: [TScrapingBot](https://t.me/TScrapingBot)

*[Readme in English](./README_ENG.md)*
</div>

## Funcionalidades

* Puedes hablar con Gemini con `/ask <mensaje>`.
* Puedes buscar en un sitio web con `/search <url del sitio> <mensaje>`.
* Puedes saber el precio del dólar en bolívares con `/dolar` (principalmente, el bot fue hecho para esto, la verdad).
* Poder discutir diversos temas en hilos separados dentro de distintos chats.
* Poder discutir sobre temas con Gemini con la capacidad de recordar mensajes.
* Poder resetear los temas por chat con `/reset`.

## Futuras Funcionalidades

* Poder escribir `/weather <lugar> <mensaje>` y recibir el clima, además de lo que pidas por el mensaje.
* Poder escribir `/lang` para configurar el idioma de las respuestas.
* Mejor control con el comando `/reset` para operaciones como resetear el historial en todos los chats existentes.
* Poder navegar por internet.
* Implementar la capacidad de Gemini para procesar imágenes.
* Poder procesar documentos y archivos de texto.
* Poder procesar videos.

## Datos y Privacidad

### Los Datos y la Experiencia

* Para que el historial y el lenguaje de las respuestas de Gemini funcionen correctamente, es necesario que el usuario esté registrado en la base de datos para obtener su idioma de preferencia antes de generar la respuesta.

* Para mantener los hilos en diferentes chats, es necesario guardar el ID del chat, ya que TScrapingBot lo utiliza para reconocer dónde está respondiendo.

* Para poder recordar conversaciones pasadas, se guardan los mensajes de entrada y salida del bot.

* El usuario se registra al ejecutar `/ask` o `/search`.

### Integridad

Los datos no serán compartidos con terceros ni utilizados para ningún otro fin que no sea el desarrollo y las funcionalidades de TScrapingBot.

## Cómo Desplegar

### Necesitarás
* Una API Key de [Gemini](https://ai.google.dev/).
* Una API Key de [Scrape.do](https://scrape.do/).
* Crear un bot con [@BotFather](https://t.me/BotFather) (en Telegram).
* Una API URL y token de [Supabase](https://supabase.com). 
  - La base de datos debe de tener esta estructura:
![Base de datos](https://cdn.discordapp.com/attachments/697811476362035251/1373732648110919741/image.png?ex=682b7bba&is=682a2a3a&hm=590764202e6392fc024ff12d65efe82aca71d6584d84b59b9956b1bed327e631&)

Lo demás varía dependiendo si lo desplegarás o lo usarás local.

Debes crear un archivo .env en la raíz del proyecto con las siguientes variables:
```env
TELEGRAM_TOKEN = <Token de Telegram>
GEMINI_TOKEN = <API de Gemini>
SCRAPEDO_TOKEN = <API key de Scrape.do>
BOT_NAME = <Nombre del bot sin @>
SUPABASE_URL = <URL de la API de Supabase>
SUPABASE_KEY = <Token de Supabase>
```

Para desplegar el bot en [Render](https://render.com/), debes añadir las variables anteriores, más las siguientes:
```env
HOSTING = true
HOST = 8080
WEBHOOK_URL = <La URL de despliegue, ej. https://mibot.onrender.com>
```