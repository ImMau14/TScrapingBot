from google import genai
from google.genai import types
import requests, json

class Gemini:
	def __init__(self, token: str, mode: str = None):
		self.client = genai.Client(api_key=token)

		try:
			with open("./data/gemini_config.json", "r", encoding="utf-8") as f:
				CONFIG = json.load(f)
		except:
			CONFIG = {}

		if mode == 'chat':
			self.mode = CONFIG.get('MarkdownV1', "")
		elif mode:
			self.mode = mode
		else:
			self.mode = CONFIG.get('Default', "")

		self.modelName = 'gemini-2.5-flash'

	def ask(self, prompt: str, photoUrl: str = None, withThoughts: bool = False) -> dict:
		try:
			contents = prompt
			if photoUrl:
				resp = requests.get(photoUrl, timeout=5)
				resp.raise_for_status()
				img_bytes = resp.content
				part = types.Part.from_bytes(
					data=img_bytes,
					mime_type="image/jpeg"
				)
				contents = [prompt, part]

			thinkingCfg = None
			if withThoughts:
				thinkingCfg = types.ThinkingConfig(
					thinking_budget=8192,
					include_thoughts=True
				)

			cfg = types.GenerateContentConfig(
				system_instruction=self.mode,
				max_output_tokens=32768,
				temperature=0.3,
				top_p=0.9,
				thinking_config=thinkingCfg
			)

			response = self.client.models.generate_content(
				model=self.modelName,
				contents=contents,
				config=cfg
			)

			if withThoughts:
				parts = response.candidates[0].content.parts
				thoughts = [p.text for p in parts if p.thought]
				answer  = next(p.text for p in parts if not p.thought)
				return {
					"thoughts": thoughts,
					"response": answer
				}
			else:
				return {"response": response.text}

		except Exception as e:
			return {"error": str(e)}