from PIL import Image
from PIL import ImageDraw, ImageFont

class ImageResizer:
    def __init__(self, size, suffix="_small", format="jpeg", keep_aspect=False, jpeg_quality=85, text=None, 
                 position="center", bg_on=True, bg_color=(0,0,0,160), max_font_size=64):
        print("init start")
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
        print("init fin")

    def make_output_name(self, filename):
        print("output_name start")
        name, _ = filename.rsplit(".", 1)
        print("output_name fin")
        return f"{name}{self.suffix}.{self.ext}"
    
    def resize_image(self, image: Image.Image) -> Image.Image:
        print("resize_image start")
        if self.keep_aspect:
            print("1")
            image = self.resize_and_crop_center(image)

        else:
            print("2")
            image = image.resize(self.size, Image.LANCZOS)
            print("2.1")

        if self.text:
            print("3")
            self.draw_text(image, self.text, self.position)
            print("4")
        print("resize_image fin")
        return image

    def resize_and_crop_center(self, image: Image.Image) -> Image.Image:
        print("crop start")
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
        print("crop fin")
        return resized.crop((left, top, right, bottom))
    
    def save_image(self, image, buf):
        print("save_image start")
        if self.format == "JPEG":
            image.save(buf, format="JPEG", quality=self.jpeg_quality)
        else:
            image.save(buf, format="PNG")
        print("fin")

    def draw_text(self, image: Image.Image, text: str, position: str = "center"):
        print("draw_text start")
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
            print("center")
            x = (img_w - text_w) // 2
            y = (img_h - text_h) // 2
        elif position == "top":
            print("top")
            x = (img_w - text_w) // 2
            y = margin
        elif position == "bottom":
            print("bottom")
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
        print("fin")

    def _get_auto_font(self, draw, text, image_width):
        print("get_auto_font start")
        font_size = self.max_font_size

        while font_size > 10:
            font = ImageFont.truetype("fonts/NotoSansJP-VariableFont_wght.ttf", font_size)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]

            if text_width <= image_width * 0.9:
                return font

            font_size -= 2
        print("fin")
        return ImageFont.truetype("fonts/NotoSansJP-VariableFont_wght.ttf", 10)

    def _load_font(self, size):
        try:
            return ImageFont.truetype(self.font_path, size)
        except Exception:
            return ImageFont.load_default()
