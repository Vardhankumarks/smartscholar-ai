from openai import OpenAI
from groq import Groq
import google.generativeai as genai

from config.config import LLM_MODELS


class LLMProvider:
    """Unified interface for multiple LLM providers."""

    def __init__(self, provider, api_key):
        self.provider = provider
        self.api_key = api_key
        self.model_name = LLM_MODELS[provider]["model"]
        self._initialize()

    def _initialize(self):
        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key)
            elif self.provider == "groq":
                self.client = Groq(api_key=self.api_key)
            elif self.provider == "google":
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
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

    def _build_google_history(self, messages):
        history = []
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        return history

    def _generate_google(self, messages, system_prompt):
        history = self._build_google_history(messages)
        prompt = messages[-1]["content"]
        if system_prompt:
            prompt = f"{system_prompt}\n\n{prompt}"

        chat = self.client.start_chat(history=history)
        response = chat.send_message(prompt)
        return response.text

    def _stream_google(self, messages, system_prompt):
        history = self._build_google_history(messages)
        prompt = messages[-1]["content"]
        if system_prompt:
            prompt = f"{system_prompt}\n\n{prompt}"

        chat = self.client.start_chat(history=history)
        response = chat.send_message(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text
