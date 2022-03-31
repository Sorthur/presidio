from asyncio.log import logger
import logging
from typing import Union, Tuple

from PIL import Image, ImageDraw, ImageChops
from presidio_analyzer import AnalyzerEngine

from presidio_image_redactor import ImageAnalyzerEngine
from presidio_analyzer.analyzer_engine import NlpEngineProvider


class ImageRedactorEngine:
    """ImageRedactorEngine performs OCR + PII detection + bounding box redaction.

    :param image_analyzer_engine: Engine which performs OCR + PII detection.
    """

    def __init__(self, image_analyzer_engine: ImageAnalyzerEngine = None):
        if not image_analyzer_engine:
            # self.image_analyzer_engine = ImageAnalyzerEngine()
            self.image_analyzer_engine = self.createImageAnalyzerEngine() #EngineImageAnalyzerEngine()
        else:
            self.image_analyzer_engine = image_analyzer_engine

    def createImageAnalyzerEngine(self) -> ImageAnalyzerEngine:
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "pl", "model_name": "pl_core_news_md"}, {"lang_code": "en", "model_name": "en_core_web_md"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_with_polish = provider.create_engine()
        engine = AnalyzerEngine(nlp_engine=nlp_engine_with_polish, supported_languages=["pl", "en"])
        return ImageAnalyzerEngine(engine)

    def redact(
        self, image: Image,
        logger2: logging.Logger,
        fill: Union[int, Tuple[int, int, int]] = (0, 0, 0),
        language: str = None,
        **kwargs,
    ) -> Image:
        """Redact method to redact the given image.

        Please notice, this method duplicates the image, creates a new instance and
        manipulate it.
        :param image: PIL Image to be processed
        :param fill: colour to fill the shape - int (0-255) for
        grayscale or Tuple(R, G, B) for RGB
        :param kwargs: Additional values for the analyze method in AnalyzerEngine

        :return: the redacted image
        """
        image = ImageChops.duplicate(image)

        bboxes = self.image_analyzer_engine.analyze(image, language, logger2, **kwargs)
        draw = ImageDraw.Draw(image)

        for box in bboxes:
            x0 = box.left
            y0 = box.top
            x1 = x0 + box.width
            y1 = y0 + box.height
            draw.rectangle([x0, y0, x1, y1], fill=fill)

        return image
