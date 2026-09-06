"""Gemini-backed inspection finding analysis."""

from app.ai.model_provider import ModelProvider
from app.models.model import ModelRequest
from app.models.model import ModelRequest
from app.services.inspection_finding_extractor import (
    InspectionFindingExtractor,
)


class GeminiInspectionAnalyzer:
    """Use the configured model provider to extract structured findings."""

    def __init__(
        self,
        model_provider: ModelProvider,
        extractor: InspectionFindingExtractor | None = None,
    ) -> None:
        self._model_provider = model_provider
        self._extractor = extractor or InspectionFindingExtractor()

    def analyze(
        self,
        inspection_text: str,
        supporting_evidence: tuple[str, ...] = (),
    ):
        if not inspection_text.strip():
            raise ValueError("inspection_text must not be empty")

        evidence = "\n\n".join(supporting_evidence)

        prompt = (
            "Analyze the following inspection report and extract only "
            "explicit inspection findings.\n\n"
            "Your response MUST contain one or more lines using exactly "
            "this format and nothing else:\n"
            "- finding: <finding> | severity: <high|medium|low> | page: <number>\n\n"
            "Do not write an introduction, explanation, markdown heading, "
            "code fence, bullets other than the required finding lines, "
            "or conclusion.\n"
            "If severity or page is unknown, omit that field.\n"
            "Do not invent findings, severity, or page numbers.\n"
            "If the report contains no explicit findings, return an empty response.\n"
            "Do not create a placeholder finding.\n\n"
            f"INSPECTION REPORT:\n{inspection_text}\n\n"
        )

        if evidence:
            prompt += (
                "SUPPORTING SOP EVIDENCE:\n"
                f"{evidence}\n"
            )

        try:
            response = self._model_provider.generate(
                ModelRequest(
                    prompt=prompt,
                )
            )
        except ValueError as exc:
            if "output must not be empty" in str(exc):
                return ()
            raise

        if not response.output.strip():
            return ()

        return self._extractor.extract(response.output)
