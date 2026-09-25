import time
from google import genai

from app.ai.model_provider import ModelProviderError
from app.config.settings import settings
from app.models.model import ModelCapability, ModelRequest, ModelResponse


class GeminiModelProvider:
    """Gemini-backed model provider for production model execution."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        client: genai.Client | None = None,
    ) -> None:
        self._model_name = model_name or settings.GEMINI_MODEL

        if client is not None:
            self._client = client
            return

        resolved_api_key = settings.GEMINI_API_KEY if api_key is None else api_key

        if not resolved_api_key:
            raise ModelProviderError("GEMINI_API_KEY is not configured.")

        self._client = genai.Client(api_key=resolved_api_key)

    @property
    def name(self) -> str:
        return self._model_name

    @property
    def capabilities(self) -> tuple[ModelCapability, ...]:
        return (
            ModelCapability.DOCUMENT,
            ModelCapability.CODE,
        )

    def generate(self, request: ModelRequest) -> ModelResponse:
        max_retries = 2
        base_delay = 1.0

        for attempt in range(max_retries + 1):
            try:
                # Use standard google-genai v2 syntax
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=request.prompt,
                )
                output = response.text

                return ModelResponse(
                    output=(output.strip() if output else ""),
                    model_name=self._model_name,
                )
            except ModelProviderError:
                raise
            except Exception as exc:
                error_str = str(exc).lower()
                is_transient = any(
                    term in error_str 
                    for term in ("503", "unavailable", "429", "too many requests", "timeout")
                )
                
                if is_transient and attempt < max_retries:
                    time.sleep(base_delay * (2 ** attempt))
                    continue
                
                raise ModelProviderError(f"Gemini generation failed: {exc}") from exc
