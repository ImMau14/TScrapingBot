import re
import requests
from bs4 import BeautifulSoup

MASKED = "token=****"

def mask_token(text, TOKEN=None):
	# Enmascara cualquier aparición de token=XYZ
	return re.sub(r'token=[^&\s]+', MASKED, text)

def obtain_page_text(_url, TOKEN=None):
	if not TOKEN:
		url = _url
	else:
		url = f"http://api.scrape.do/?token={TOKEN}&url={_url}"

	try:
		resp = requests.get(url, timeout=10)
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, 'html.parser')
		return soup.get_text(separator='\n', strip=True)

	# except requests.exceptions.HTTPError as e:
		# Extrae el código y el mensaje original
		# code = e.response.status_code
		# reason = e.response.reason
		# err_url = mask_token(e.request.url)
		# if code == 400:
			# return "Error 400: solicitud malformada."
		# return f"HTTP {code} {reason} al acceder a {err_url}"

	# except requests.exceptions.RequestException as e:
		# Captura timeouts, rechazos, DNS, etc.
		# err = mask_token(str(e))
		# return f"Error de red: {err}"

	except Exception as e:
		# Cualquier otro fallo
		# err = mask_token(str(e))
		return f"Error interno."

if __name__ == "__main__":
	texto = obtain_page_text("https://www.google.com")
	print(texto)