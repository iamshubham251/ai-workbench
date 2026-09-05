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
        try:
            interaction = self._client.interactions.create(
                model=self._model_name,
                input=request.prompt,
            )
            output = interaction.output_text

            if not output or not output.strip():
                raise ModelProviderError("Gemini returned an empty response.")

            return ModelResponse(
                output=output.strip(),
                model_name=self._model_name,
            )
        except ModelProviderError:
            raise
        except Exception as exc:
            raise ModelProviderError(f"Gemini generation failed: {exc}") from exc
