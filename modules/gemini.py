import google.generativeai as genai
import json

with open("./gemini_config.json", "r", encoding="utf-8") as f:
	CONFIG = json.load(f)

class Gemini:
	def __init__(self, token, mode=None):
		genai.configure(api_key=token)

		if mode == 'chat':
			self.mode = CONFIG['MarkdownV1']
		elif mode:
			self.mode = mode
		else:
			self.mode = CONFIG['Default']

		self.modelo = genai.GenerativeModel(
			'gemini-2.0-flash',
			system_instruction=self.mode,
			generation_config=genai.GenerationConfig(
				max_output_tokens=4000,
				temperature=0.3,
				top_p=0.9,
			)
		)

	def ask(self, prompt):
		try:
			respuesta = self.modelo.generate_content(prompt)
			return respuesta.text
		except Exception as e:
			return f"Error: {str(e)}"
