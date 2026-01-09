import streamlit as st
import io
import zipfile
import logging
from PIL import Image
from PIL import ImageOps
from typing import List
from streamlit.runtime.uploaded_file_manager import UploadedFile
from resize_core import ImageResizer


logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

FONT_OPTIONS = {
    "ゴシック（太・目立つ）": {
        "path": "fonts/NotoSansJP-Bold.ttf",
        "default_size": 72
    },
    "ゴシック（標準）": {
        "path": "fonts/NotoSansJP-Regular.ttf",
        "default_size": 56
    },
    "丸ゴシック（やさしい）": {
        "path": "fonts/MPLUSRounded1c-Regular.ttf",
        "default_size": 60
    }
}


def build_zip_from_images(
    files: List[UploadedFile],
    resizer: ImageResizer,
    format: str,
) -> io.BytesIO:
    zip_buf = io.BytesIO()

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for uploaded_file in files:
            try:
                image = Image.open(uploaded_file)
                image = ImageOps.exif_transpose(image)

                with st.spinner("画像を変換しています..."):
                    resized = resizer.resize_image(image.copy())

            except Exception as e:
                logger.exception("画像変換エラー")
                st.error("画像の変換に失敗しました。別の画像を試してください。")
                continue

            img_buf = io.BytesIO()

            if format == "JPEG":
                resized.save(img_buf, format="JPEG", quality=85)
            else:
                resized.save(img_buf, format="PNG")

            img_buf.seek(0)

            output_name = resizer.make_output_name(uploaded_file.name)
            zip_file.writestr(output_name, img_buf.read())

    zip_buf.seek(0)
    return zip_buf

DEFAULT_WIDTH = 1200
DEFAULT_HEIGHT = 630

width = DEFAULT_WIDTH
height = DEFAULT_HEIGHT

SIZE_PRESETS = {
    "カスタム": None,
    "note・YouTubeサムネ（1280×720）": (1280, 720),
    "ブログOGP（1200×630）": (1200, 630),
    "X（旧Twitter）（1200×675）": (1200, 675),
}

keep_aspect: bool = False
text: str = None
font_path: str = None
text_color: str = "white"
#stroke_width: int = 3
position: str = "top"
bg_color: tuple = (0,0,0,160)
bg_alpha: int = 160
font_size: int = 64
suffix: str = "_thumb"
format: str = "JPEG"
jpeg_quality: int = 85

st.title("ブログ用サムネ画像リサイズ")
st.caption("note・ブログ用のサムネ画像を、サイズ崩れなく一括生成できます")


uploaded_files = st.file_uploader(
        "画像をアップロード（複数可）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)
left, right = st.columns([1, 1])
with left:
    if uploaded_files:
        with st.expander("サイズ設定", expanded=True):
#    if "preset_name" not in st.session_state:
#        st.session_state.preset_name = "カスタム"

            preset_name = st.selectbox("サイズプリセット", options=list(SIZE_PRESETS.keys()), key="preset_name")

            if st.session_state.preset_name != "カスタム":
                preset_size = SIZE_PRESETS[st.session_state.preset_name]
                width, height = preset_size
            else:
                width = st.slider( "幅 (px)", min_value=300, max_value=2000, value=width, step=10)
                height = st.slider( "高さ (px)", min_value=300, max_value=2000, value=height, step=10)
            keep_aspect = st.checkbox("縦横比を維持する", value=True)
#        st.markdown("---")
        with st.expander("テキスト設定", expanded=False):
            text = st.text_input("追加する文字（空欄なら追加しません）", "")
            if text:
                font_label = st.selectbox("フォント（日本語向け）", options=list(FONT_OPTIONS.keys()))
                font_info = FONT_OPTIONS[font_label]
                font_path = font_info["path"]
                default_font_size = font_info["default_size"]
#        stroke_width = st.slider( "文字の縁取りの太さ", min_value=0, max_value=10, value=3)
#        stroke_width = st.slider("文字の縁取り（0=OFF）", 0, 10, 5)
                text_color = st.color_picker("文字色", "#FFFFFF")
                position = st.selectbox("文字位置", ["center", "top", "bottom"])
                bg_color = st.color_picker("背景色", "#000000")
                bg_alpha = st.slider("文字背景の透過度", min_value=0, max_value=255, value=160)
                font_size = st.slider("最大フォントサイズ", 20, 100, 64)

        resizer = ImageResizer(
            size=(width, height),
            keep_aspect=keep_aspect,
            jpeg_quality=jpeg_quality,
            text=text,
            text_color=text_color,
#        stroke_width=stroke_width,
            position=position,
            bg_color=bg_color,
            bg_alpha=bg_alpha,
            font_size=font_size,
            font_path=font_path,
            suffix=suffix,
            format=format,
        )

with right:
    if uploaded_files:
    # サンプル画像表示
        first_file = uploaded_files[0]
        image = Image.open(first_file)
        image = ImageOps.exif_transpose(image)
        preview = resizer.resize_image(image)

        st.subheader("プレビュー")
        st.image(preview, width=400)
        with st.expander("保存設定", expanded=False):
            suffix = st.text_input("ファイル名（下のtextを末尾に追加して保存）", value="_thumb")
            format = st.selectbox("保存形式", ["JPEG", "PNG"], index=0)
            if format == "JPEG":
                jpeg_quality = st.slider("JPEG品質", 50, 95, 85)
            zip_buf = build_zip_from_images(uploaded_files, resizer, format)

        st.download_button(
            label="ZIPでまとめてダウンロード",
            data=zip_buf,
            file_name="resized_images.zip",
            mime="application/zip"
        )
