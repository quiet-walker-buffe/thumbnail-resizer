import streamlit as st
import io
import zipfile
from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw, ImageFont
from resize_core import ImageResizer

def build_zip_from_images(files, resizer, format):
    zip_buf = io.BytesIO()

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for uploaded_file in files:
            try:
                image = Image.open(uploaded_file)
                image = ImageOps.exif_transpose(image)

                with st.spinner("画像を変換しています..."):
                    resized = resizer.resize_image(image.copy())

            except Exception:
                st.error("画像の変換に失敗しました。別の画像を試してください。")
                continue  # ← 重要

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

st.title("ブログ用サムネ画像リサイズ（複数対応）")

uploaded_files = st.file_uploader(
    "画像をアップロード（複数可）",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

# 設定受付
width = st.number_input("幅 (px)", min_value=50, max_value=3000, value=1200)
height = st.number_input("高さ (px)", min_value=50, max_value=3000, value=630)
suffix = st.text_input("ファイル名サフィックス", value="_thumb")
format = st.selectbox("保存形式", ["JPEG", "PNG"], index=0)
keep_aspect = st.checkbox("縦横比を維持する", value=True)
if format == "JPEG":
    jpeg_quality = st.slider("JPEG品質", 50, 95, 85)
else:
    jpeg_quality = None
text = st.text_input("追加する文字（空欄なら追加しません）", "")
position = st.selectbox("文字位置", ["center", "bottom", "top"], index=0)
bg_on = st.checkbox("背景をつける", value=True)
bg_color = st.color_picker("背景色", "#000000")
max_font_size = st.slider("最大フォントサイズ", 20, 100, 64)

if uploaded_files:
    resizer = ImageResizer(
        size=(width, height),
        suffix=suffix,
        format=format,
        keep_aspect=keep_aspect,
        jpeg_quality=jpeg_quality,
        text=text,
        position=position,
        bg_on=bg_on,
        bg_color=bg_color,
        max_font_size=max_font_size
    )

    zip_buf = build_zip_from_images(uploaded_files, resizer, format)

    st.download_button(
        label="ZIPでまとめてダウンロード",
        data=zip_buf,
        file_name="resized_images.zip",
        mime="application/zip"
    )
