import re
import requests
from bs4 import BeautifulSoup

def mask_token(text):
	return re.sub(r'token=[^&\s]+', "token=****", text)

def obtainPageText(_url, TOKEN=None):
	if not TOKEN:
		url = _url
	else:
		url = f"http://api.scrape.do/?token={TOKEN}&url={_url}"

	try:
		resp = requests.get(url, timeout=10)
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, 'html.parser')
		return soup.get_text(separator='\n', strip=True)

	except requests.exceptions.HTTPError as e:
		# Extrae el código y el mensaje original
		code = e.response.status_code
		reason = e.response.reason
		err_url = mask_token(e.request.url)
		if code == 400:
			return "Error 400: solicitud malformada."
		return f"HTTP {code} {reason} al acceder a {err_url}"

	except requests.exceptions.RequestException as e:
		# Captura timeouts, rechazos, DNS, etc.
		err = mask_token(str(e))
		return f"Error de red: {err}"

	except Exception as e:
		# Cualquier otro fallo
		err = mask_token(str(e))
		return f"Error interno: {e}."

if __name__ == "__main__":
	texto = obtainPageText("https://www.google.com")
	print(texto)