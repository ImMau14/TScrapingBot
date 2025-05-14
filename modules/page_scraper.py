import requests
from bs4 import BeautifulSoup

def obtainPageText(url):
	try:
		response = requests.get(url)
		response.raise_for_status()
		soup = BeautifulSoup(response.text, 'html.parser')
		texto = soup.get_text(separator='\n', strip=True)
		return texto
	except requests.exceptions.RequestException as e:
		return f"Network error: {e}"
	except Exception as e:
		return f"Error: {e}"

if __name__ == "__main__":
	url = "https://www.google.com"
	texto_visible = obtainPageText(url)
	print(texto_visible)
