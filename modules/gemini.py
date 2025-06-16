import google.generativeai as genai
import requests, os

try:
	with open("./data/gemini_config.json", "r", encoding="utf-8") as f:
		from json import load
		CONFIG = load(f)
except Exception as e:
	print("Failed to load gemini_config.json\nYou will need to specify the mode when initializing the class to avoid errors\nDetails: ", str(e))

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

	# Recomended: .jpg format for images.
	def ask(self, prompt, photoUrl = None):
		try:
			if photoUrl:
				imageBytes = requests.get(photoUrl).content
				with open(photoUrl.split("/")[-1], "wb") as f:
					f.write(imageBytes)

				uploadedImage = genai.upload_file(path=photoUrl.split("/")[-1], display_name=photoUrl.split("/")[-1])
				os.remove(photoUrl.split("/")[-1])
				return self.modelo.generate_content([prompt, uploadedImage]).text
			else:
				return self.modelo.generate_content(prompt).text
		except Exception as e:
			return f"Error: {str(e)}"