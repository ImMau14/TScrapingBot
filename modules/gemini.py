import google.generativeai as genai

class Gemini:
	def __init__(self, token):
		genai.configure(api_key=token)
		self.modelo = genai.GenerativeModel('gemini-2.0-flash')

	def ask(self, prompt):
		try:
			respuesta = self.modelo.generate_content(prompt)
			return respuesta.text
		except Exception as e:
			return f"Error: {str(e)}"