"""
Script responsável por criar as imagens das obras com as anotações
definidas pelos alunos durante o processo de classificação.
"""
from constants import IMAGES_DIR, OFFLINE_IMGS_DIR, CAPTIONS_DIR, CAPTIONS_REVERSE, MOSAIC_DIR

from pathlib import Path
import cv2
import random
import wcag_contrast_ratio as contrast
from PIL import Image, ImageDraw, ImageFont

font_face = cv2.FONT_HERSHEY_SIMPLEX
scale = 2
thickness = 2
baseline = cv2.LINE_AA
BLACK = (17, 17, 17)
TEXT_SIZE = 48


CATEGORY_COLORS = {}


def get_image_path(item):
    image_path = IMAGES_DIR / f"{item}.jpg"
    if not image_path.exists():
        image_path = OFFLINE_IMGS_DIR / f"{item}.jpg"
    return image_path


def get_caption_image_path(row):
    img_dir = CAPTIONS_REVERSE[row.categoria]
    return MOSAIC_DIR / img_dir / row.imagem


def tag_image(item, annotations):
    image_path = get_image_path(item)
    out_img = (CAPTIONS_DIR / f"{item}.jpg").resolve()
    if out_img.exists():
        return

    img_pil = Image.open(str(image_path.resolve()))

    # lógica para determinar tamanho da fonte em relação
    # ao caption com maior texto
    big_text = ""
    for annotation in annotations:
        if len(annotation.categoria) > len(big_text):
            big_text = annotation.categoria

    img_fraction = 0.1  # proporção do texto em relação a largura
    font_size = 1  # tamanho inicial
    font_name = "DejaVuSansCondensed-Bold.ttf"
    font = ImageFont.truetype(font_name, font_size)

    # incrementa o tamanho da fonte até ficar na proporçao desejada
    while font.getsize(big_text)[0] < img_fraction * img_pil.size[0]:
        font_size += 1
        font = ImageFont.truetype(font_name, font_size)

    draw = ImageDraw.Draw(img_pil)
    for annotation in annotations:
        text = annotation.categoria
        x1, y1, x2, y2 = [int(c) for c in annotation.area.split(',')]
        p1, p2 = (x1, y1), (x2, y2)
        text_p = (p1[0], p1[1])
        color = get_valid_color(text)

        box = draw.textbbox(text_p, text, font=font, stroke_width=2)
        draw.rectangle(box, fill=color, outline=color, width=2)
        draw.rectangle((p1, p2), outline=color, width=2)
        draw.text(text_p, text, font=font, fill=BLACK)

    out_path = str(out_img.resolve())
    img_pil.save(out_path, quality=80)


def get_valid_color(category, min_contrast_ratio=4.5, text_color=BLACK):
    """
    Only picks color with a contrast ratio higher than 4.5 by default
    More info here: https://www.w3.org/TR/WCAG20-TECHS/G18.html
    """
    if category not in CATEGORY_COLORS:

        contrast_ration = 0
        while contrast_ration < min_contrast_ratio:
            color_range = range(255)
            color = (
                random.choice(color_range),
                random.choice(color_range),
                random.choice(color_range),
            )
            if color in CATEGORY_COLORS.values():
                continue
            contrast_ration = contrast.rgb_as_int(text_color, color)
        CATEGORY_COLORS[category] = color
    return CATEGORY_COLORS[category]
