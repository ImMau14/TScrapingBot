import requests

async def get_dolar_values():
	url = "https://api.alcambio.app/graphql"

	query = [
		"query GetCountryConversions($payload: GetConversionsInput!) {",
		"  getCountryConversions(payload: $payload) {",
		"    _id",
		"    baseCurrency { code name symbol }",
		"    country { name code }",
		"    conversionRates {",
		"      baseValue",
		"      rateCurrency { code name }",
		"      type",
		"    }",
		"  }",
		"}"
	]

	variables = {
		"payload": {
			"countryCode": "VE"
		}
	}

	headers = {
		"Content-Type": "application/json",
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
	}

	response = requests.post(
		url,
		json={"query": '\n'.join(query), "variables": variables},
		headers=headers
	)

	if response.status_code == 200:
		bcv = response.json()['data']['getCountryConversions']['conversionRates'][1]['baseValue']
		paralelo = response.json()['data']['getCountryConversions']['conversionRates'][0]['baseValue']
		promedio = round((bcv + paralelo) / 2, 2)

		return {
			'dolar-bcv' : bcv,
			'dolar-par' : paralelo,
			'dolar-pro' : promedio
		}

	else:
		return {
			'error' : response.status_code,
			'details' : response.text
		}