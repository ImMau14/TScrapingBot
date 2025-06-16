# 🕸 TScrapingBot 1.4.0

![Python](https://img.shields.io/badge/Python-001f2d?style=for-the-badge\&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-041453?style=for-the-badge\&logo=telegram\&logoColor=046dac)
![Flask](https://img.shields.io/badge/Flask-010101?style=for-the-badge\&logo=flask)
![Gemini](https://img.shields.io/badge/Gemini-00436b?style=for-the-badge\&logo=googlegemini\&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-27273e?style=for-the-badge\&logo=postgresql)
![Requests](https://img.shields.io/badge/Requests-white?style=for-the-badge\&logo=python\&logoColor=black)
![Beautiful Soup](https://img.shields.io/badge/Beautiful%20Soup-black?style=for-the-badge\&logo=python\&logoColor=white)

Un bot de Telegram para web scraping potenciado con inteligencia artificial. Clic aquí para usarlo en Telegram: [@TScrapingBot](https://t.me/TScrapingBot)

*[Readme in English](./README_ENG.md)*

## 🌟 Características

### ✅ Actuales

* Respuestas de texto generadas por Gemini 2.0.
* Análisis de imagen.
* Fetching y análisis de contenido de URL's.
* Memoria en chats (solo comandos `/ask` y `/search`).
* Obtener el precio del USD en VES.

### 🔮 Futuras

* Generación de imágenes.
* Conversación mediante audios.
* Chats colectivos en grupos.
* Procesar documentos de texto y archivos de video.
* Obtener el clima.
* Navegar entre repositorios de GitHub.

## 📜 Comandos

|          Comando         |                      Acción                     |
| :----------------------: | :---------------------------------------------: |
|         `/start`         |                Comando de inicio                |
|          `/ping`         |   Comando para saber si el bot está despierto   |
|          `/help`         |         Muestra los comandos disponibles        |
|         `/dolar`         | Muestra el precio actual del dólar en bolívares |
|      `/ask <prompt>`     |                Pregunta a Gemini                |
|         `/reset`         |          Resetea el historial de chat           |
| `/search <url> <prompt>` |  Busca en la URL y pregunta a Gemini sobre eso  |

## 🚀 Despliegue

### ⚙️ Requisitos

* Python 3.11.\* (o superior).
* API key de [Gemini 2.0](https://ai.google.dev/).
* Crear un bot con [@BotFather](https://t.me/BotFather) y obtener su token (en Telegram).
* Token de [Scrape.do](https://scrape.do/).
* Base de datos, Token y URL de [Supabase](https://supabase.com).

### 🗃️ Base de Datos

Debe de tener esta estructura (código SQL en [schema.sql](data/schema.sql)):

![Diagrama de Supabase](https://files.catbox.moe/a1xva7.png)

### 🔐 Variables de Entorno

#### 🧱 Básicas

|     Variable     |         Valor         |
| :--------------: | :-------------------: |
|  `GEMINI_TOKEN`  |   Tu token de Gemini  |
| `SCRAPEDO_TOKEN` | Tu token de Scrape.do |
|  `SUPABASE_KEY`  |  Tu token de Supabase |
|  `SUPABASE_URL`  |   Tu URL de Supabase  |
| `TELEGRAM_TOKEN` |  Tu token de Telegram |

#### 🛠️ Para Producción

|    Variable   |     Valor    |
| :-----------: | :----------: |
|   `HOSTING`   |    `true`    |
| `WEBHOOK_URL` | URL del host |

### 📦 Instalación

**En estos pasos se asume que ya se ha creado la base de datos.**

1. Clona y entra en el repositorio:

```bash
git clone https://github.com/ImMau14/TScrapingBot
cd TScrapingBot
```

2. Inicia un entorno virtual e instala las dependencias:

```bash
# En Linux/macOS
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

```bash
# En Windows
python -m venv env
.\env\Scripts\activate
pip install -r requirements.txt
```

3. Copia y configura las variables de entorno.

```bash
cp .env.template .env
nano .env # O el editor de tu preferencia.
```

4. Enciende el bot:

```bash
# En Linux/macOS
python3 main.py
```

```bash
# En Windows
python main.py
```

## 🗂️ Estructura

```
TScrapingBot/
├── data/
│   ├── gemini_config.json    # Modos de configuración de Gemini
│   ├── messages.json         # Mensajes del bot
│   └── schema.sql            # Tablas de la base de datos
├── modules/
│   ├── database.py           # Funciones de base de datos
│   ├── dolar_scraper.py      # Función scraper del dólar
│   ├── gemini.py             # Clase manejadora de Gemini
│   ├── page_scraper.py       # Función scraper de webs
│   └── utils.py              # Funciones útiles
├── main.py                   # Archivo principal (bot)
├── requirements.txt          # Dependencias
├── .env.template             # Plantilla de variables de entorno
├── .gitignore                # Git Ignore
├── README_ENG.md             # README en inglés
├── README.MD                 # README en español
└── LICENSE                   # Licencia MIT
```

## ☁️ Desplegado En

* Host: [Render](https://render.com).
* Base de datos: [Supabase](https://supabase.com).

## 📜 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.
