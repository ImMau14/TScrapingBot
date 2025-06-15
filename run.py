import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from main import app, bot_app

load_dotenv()

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def main():
	await bot_app.initialize()
	await bot_app.start()

	webhook_full_url = f"{os.getenv('WEBHOOK_URL')}/webhook"
	await bot_app.bot.set_webhook(
		url=webhook_full_url,
		allowed_updates=Update.ALL_TYPES
	)
	logging.info(f"Webhook set to: {webhook_full_url}")

	port = int(os.environ.get("PORT", 8080))
	logging.info(f"Starting HTTP server on 0.0.0.0:{port}")
	await app.run_task(host="0.0.0.0", port=port)

if __name__ == "__main__":
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logging.info("Server stopped manually.")
	except Exception as e:
		logging.error(f"Fatal error: {e}", exc_info=True)
