from typing import Optional, Tuple
from PIL import Image
from PIL import ImageDraw, ImageFont
from pathlib import Path
import logging

BASE_DIR = Path(__file__).resolve().parent
FONT_PATH = BASE_DIR / "fonts" / "NotoSansJP-VariableFont_wght.ttf"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageResizer:
    def __init__(
        self,
        size: Tuple[int, int],
        suffix: str = "_small",
        format: str = "jpeg",
        keep_aspect: bool = False,
        jpeg_quality: Optional[int] = 85,
        text: Optional[str] = None,
        position: str = "center",
        bg_on: bool = True,
        bg_color: Tuple[int, int, int, int] = (0, 0, 0, 160),
        max_font_size: int = 64,
    ) -> None:

        logger.debug("init start")
        self.size = size
        self.suffix = suffix
        self.format = format
        self.keep_aspect = keep_aspect
        self.ext = format.lower()
        self.jpeg_quality = jpeg_quality
        self.text = text
        self.position = position
        self.bg_on = bg_on
        self.bg_color = bg_color
        self.max_font_size = max_font_size
        logger.debug("init end")

    def make_output_name(self, filename: str) -> str:
        logger.debug("output_name start")
        name, _ = filename.rsplit(".", 1)
        logger.debug("output_name end")
        return f"{name}{self.suffix}.{self.ext}"
    
    def resize_image(self, image: Image.Image) -> Image.Image:
        logger.debug("resize_image start")

        if self.keep_aspect:
            logger.debug("1")
            image = self.resize_and_crop_center(image)

        else:
            logger.debug("2")
            image = image.resize(self.size, Image.LANCZOS)

        if self.text:
            logger.debug("3")
            self.draw_text(image, self.text, self.position)
        logger.debug("resize_image end")
        return image

    def resize_and_crop_center(self, image: Image.Image) -> Image.Image:
        logger.debug("crop start")
        src_w, src_h = image.size
        target_w, target_h = self.size

        # 拡大率を決める（足りない辺基準）
        scale = max(target_w / src_w, target_h / src_h)

        new_w = int(src_w * scale)
        new_h = int(src_h * scale)

        resized = image.resize((new_w, new_h), Image.LANCZOS)

        # 中央トリミング位置
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        logger.debug("crop end")
        return resized.crop((left, top, right, bottom))
    
    def save_image(self, image, buf):
        logger.debug("save_image start")
        if self.format == "JPEG":
            image.save(buf, format="JPEG", quality=self.jpeg_quality)
        else:
            image.save(buf, format="PNG")
        logger.debug("save_image end")

    def draw_text(self, image: Image.Image, text: str, position: str = "center") -> None:
        logger.debug("draw_text start")
        draw = ImageDraw.Draw(image, "RGBA")
        img_w, img_h = image.size
        font = self._get_auto_font(draw, text, img_w)
        
        # テキストサイズ取得
        bbox = draw.textbbox((0, 0), text, font=font)
        left, top, right, bottom = bbox
        text_w = right - left
        text_h = bottom - top
        margin = 20
        padding = 10  # 背景の余白

        if position == "center":
            logger.debug("draw_text: center position")

            x = (img_w - text_w) // 2
            y = (img_h - text_h) // 2
        elif position == "top":
            logger.debug("draw_text: top")
            x = (img_w - text_w) // 2
            y = margin
        elif position == "bottom":
            logger.debug("draw_text: bottom")
            x = (img_w - text_w) // 2
            y = img_h - text_h - margin
        else:
            x = (img_w - text_w) // 2
            y = (img_h - text_h) // 2

        # 背景帯（半透明）
        rect = (
            x - padding,
            y - padding,
            x + text_w + padding,
            y + text_h + padding
        )
        if self.bg_on:
            draw.rectangle(rect, fill=(0, 0, 0, 160))
        text_x = x - left
        text_y = y - top
        # 文字
        draw.text((text_x, text_y), text, fill="white", font=font)
        logger.debug("draw_text end")

    def _get_auto_font(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        image_width: int,
    ) -> ImageFont.FreeTypeFont:
        font_size = self.max_font_size

        while font_size > 10:
            font = ImageFont.truetype(str(FONT_PATH), font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= image_width * 0.9:
                return font

            font_size -= 2

        return ImageFont.truetype(str(FONT_PATH), 10)


    def _load_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception:
            return ImageFont.load_default()
