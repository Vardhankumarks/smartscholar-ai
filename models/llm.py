from openai import OpenAI
from groq import Groq
from google import genai

class LLMProvider:
    """Unified interface for multiple LLM providers."""

    def __init__(self, provider, api_key, model_name):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self._initialize()

    def _initialize(self):
        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key)
            elif self.provider == "groq":
                self.client = Groq(api_key=self.api_key)
            elif self.provider == "google":
                self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize {self.provider}: {e}")

    def generate(self, messages, system_prompt=""):
        """Generate a complete response (non-streaming)."""
        try:
            if self.provider in ("openai", "groq"):
                return self._generate_openai_compatible(messages, system_prompt)
            elif self.provider == "google":
                return self._generate_google(messages, system_prompt)
        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")

    def generate_stream(self, messages, system_prompt=""):
        """Generate a streaming response."""
        try:
            if self.provider in ("openai", "groq"):
                yield from self._stream_openai_compatible(messages, system_prompt)
            elif self.provider == "google":
                yield from self._stream_google(messages, system_prompt)
        except Exception as e:
            raise RuntimeError(f"LLM streaming failed: {e}")

    def _build_openai_messages(self, messages, system_prompt):
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)
        return full_messages

    def _generate_openai_compatible(self, messages, system_prompt):
        full_messages = self._build_openai_messages(messages, system_prompt)
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
        )
        return response.choices[0].message.content

    def _stream_openai_compatible(self, messages, system_prompt):
        full_messages = self._build_openai_messages(messages, system_prompt)
        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=full_messages,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _build_google_contents(self, messages, system_prompt):
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        if system_prompt and contents:
            first_text = contents[0]["parts"][0]["text"]
            contents[0]["parts"][0]["text"] = f"{system_prompt}\n\n{first_text}"
        return contents

    def _generate_google(self, messages, system_prompt):
        contents = self._build_google_contents(messages, system_prompt)
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=contents,
        )
        return response.text

    def _stream_google(self, messages, system_prompt):
        contents = self._build_google_contents(messages, system_prompt)
        response = self.client.models.generate_content_stream(
            model=self.model_name,
            contents=contents,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
