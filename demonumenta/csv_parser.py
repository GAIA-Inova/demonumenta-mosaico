"""
Módulo responsável por organizar o código que manipula as entradas da planilha de repostas
"""
import shutil
import re
import io
import os
import requests
import urllib
from pathlib import Path
from PIL import Image

from constants import (
    CAPTIONS,
    IMG_URL_COL,
    IMAGES_DIR,
    ITEM_URL_COL,
    SPLIT_TOKEN,
    MOSAIC_DIR,
    OFFLINE_IMGS_DIR,
)


class UnexistingImageException(Exception):
    pass


def download_image(item, image_url, from_local=False):
    """
    Baixa a imagem do acervo, caso ela ainda não exista em disco
    """
    if from_local:
        image_path = OFFLINE_IMGS_DIR / f"{item}.jpg"
        image_url = f"file://{image_path.resolve()}"

    suffix = Path(image_url).suffix or ".jpg"
    image_path = IMAGES_DIR / f"{item}{suffix}"
    if image_path.exists():
        return image_path

    # para obras que não estão na wikimedia e buscamos no google
    if from_local:
        src_img = OFFLINE_IMGS_DIR / f"{item}.jpg"
        if not src_img.exists():
            raise UnexistingImageException(f"Imagem do item {item} não existe no diretório de imagens extras")
        shutil.copy(src_img, image_path)
        return image_path

    # para obras que estão na wikimedia ou outra URL
    response = requests.get(image_url, allow_redirects=True)
    if not response.ok:
        raise UnexistingImageException(f"Não conseguiu baixar para o item {item} a url {image_url}")

    with Image.open(io.BytesIO(response.content)) as im:
        im.save(
            image_path,
            format="JPEG",
            quality="maximum",
            icc_profile=im.info.get("icc_profile"),
        )

    return image_path


def process_image(data, image_path):
    """
    Gera todas as imagens de caixas marcadas para a imagem
    """
    for caption in CAPTIONS:
        coords = data[caption]
        if not coords:
            continue

        caption_dir = MOSAIC_DIR / caption
        if not caption_dir.exists():
            os.mkdir(caption_dir.resolve())

        item_id = data["item_id"]
        image = Image.open(image_path)

        for i, area in enumerate(coords):
            out_img = caption_dir / f"{item_id}-{caption}-{i:0>2d}.jpg"
            if out_img.exists():
                continue
            crop = image.crop(area)
            crop.save(
                out_img,
                quality="maximum",
                icc_profile=image.info.get("icc_profile"),
            )

        image.close()


def clean_row(row):
    """
    Sanitiza e organiza os dados de entrada
    """
    errors_list = []

    entry = row._asdict()
    img_url = entry[IMG_URL_COL]
    # alguns colaboradores colocaram somente o código Q ao invés da URL para o item
    if entry[ITEM_URL_COL].startswith("Q"):
        item_id = entry[ITEM_URL_COL].strip()
        entry[IMG_URL_COL] = f"http://www.wikidata.org/entity/{item_id}"

    item_url = urllib.parse.urlparse(entry[ITEM_URL_COL])
    item_id = item_url.path.split("/")[-1]
    entry["item_id"] = item_id
    entry["img_url"] = img_url

    should_skip = False
    email_regex = "^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$"
    if img_url.strip() == "imagem do computador" or "drive.google.com" in img_url:
        entry["local_file"] = True
    # esses são erros que impedem o processamento da imagem já que não podemos baixá-la
    if re.search(email_regex, img_url):
        errors_list.append("Link da imagem com email (respostas antigas)")
        should_skip = True
    if not item_id.startswith("Q"):
        errors_list.append("Link do item está errado (provavelmente com link da imagem)")
        should_skip = True

    for caption in CAPTIONS:
        # sanitiza as captions para serem listas de coordenadas
        try:
            entry[caption] = [
                [int(n) for n in c.strip().split(",")]
                for c in (entry[caption] or "").strip().split(SPLIT_TOKEN)
                if c.strip()
            ]
        except ValueError:
            entry[caption] = []
            errors_list.append(
                f"Categoria {caption} com valores mal formatados (quebras de linha, texto sem numero, mal separador...)"
            )

    # garante que todas as coordenadas possuem somente 4 valores
    for caption in CAPTIONS:
        invalid_coords = []
        coords = entry[caption]
        if not coords:
            continue
        for coord in coords:
            # cada tupla de coordenada deve ter somente 4 valores
            invalid = False
            if len(coord) > 4:
                errors_list.append(f"Categoria {caption} com área de corte com mais de 4 pontos.")
                invalid = True
            if len(coord) < 4:
                errors_list.append(f"Categoria {caption} com área de corte com menos de 4 pontos.")
                invalid = True

            if invalid:
                invalid_coords.append(coord)
            else:
                # garante ordenação no eixo X (primeira coordenada deve ser x e a outra é x + diff)
                if coord[0] > coord[2]:
                    coord[0], coord[2] = coord[2], coord[0]
                # garante ordenação no eixo Y (primeira coordenada deve ser y e a outra é y + diff)
                if coord[1] > coord[3]:
                    coord[1], coord[3] = coord[3], coord[1]

        for invalid in invalid_coords:
            entry[caption].remove(invalid)

    return entry, errors_list, should_skip
