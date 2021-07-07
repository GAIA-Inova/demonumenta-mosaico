"""
Script responsável por criar as imagens das obras com as anotações
definidas pelos alunos durante o processo de classificação.
"""
from constants import IMAGES_DIR, OFFLINE_IMGS_DIR, CAPTIONS_DIR

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


def tag_image(item, annotations):
    image_path = get_image_path(item)
    out_img = (CAPTIONS_DIR / f"{item}.jpg").resolve()
    if out_img.exists():
        return

    out_path = str(out_img.resolve())
    image = cv2.imread(str(image_path.resolve()))
    for annotation in annotations:
        x1, y1, x2, y2 = [int(c) for c in annotation.area.split(',')]
        p1, p2 = (x1, y1), (x2, y2)
        image = tag_element(image, p1, p2, annotation.categoria)

    cv2.imwrite(out_path, image, [cv2.IMWRITE_JPEG_QUALITY, 80])

    # esse hack é porque o open-cv não renderiza caracteres utf-8
    font = ImageFont.truetype("DejaVuSansCondensed-Bold.ttf", 58)
    img_pil = Image.open(out_path)
    draw = ImageDraw.Draw(img_pil)
    for annotation in annotations:
        x1, y1, x2, y2 = [int(c) for c in annotation.area.split(',')]
        p1, p2 = (x1, y1), (x2, y2)
        text_p = (p1[0], p1[1])
        draw.text(text_p, annotation.categoria, font=font, fill=BLACK)

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


def tag_element(img, p1, p2, tag):
    """
    p1 = (x1, y1)
    p2 = (x2, y2) from the rectangle
    More here: https://stackoverflow.com/questions/23720875/how-to-draw-a-rectangle-around-a-region-of-interest-in-python
    """
    text_p = (p1[0], p1[1] + TEXT_SIZE)

    size = cv2.getTextSize(tag, font_face, scale, thickness)
    label_background_start = (text_p[0], text_p[1] - TEXT_SIZE)
    label_background_pos = (
        label_background_start[0] + size[0][0],
        label_background_start[1] + size[0][1] + 16,
    )

    color = get_valid_color(tag)
    cv2.rectangle(img, p1, p2, color, 2)
    cv2.rectangle(img, label_background_start, label_background_pos, color, -1)
    #cv2.putText(img, tag, text_p, font_face, scale, BLACK, thickness, baseline)

    return img
