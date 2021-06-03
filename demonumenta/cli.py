#!/usr/bin/env python3

import io
import click
import os
import requests
import rows
import urllib
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from constants import (
    CAPTIONS,
    IMG_URL_COL,
    ITEM_URL_COL,
    IMAGES_DIR,
    ITEM_URL_COL,
    SPLIT_TOKEN,
    MOSAIC_DIR,
)


@click.group()
def command_line_entrypoint():
    """
    Ferramenta pra explorar imagens do dataset Open Images V6
    """
    pass


def download_image(item, image_url):
    """
    Baixa a imagem do acervo, caso ela ainda não exista em disco
    """
    suffix = Path(image_url).suffix or ".jpg"
    image_path = IMAGES_DIR / f"{item}{suffix}"

    if image_path.exists():
        return image_path

    response = requests.get(image_url, allow_redirects=True)
    if not response.ok:
        print(f"Não conseguiu baixar a url {image_url}")

    with Image.open(io.BytesIO(response.content)) as im:
        im.save(image_path, format="JPEG", quality="maximum", icc_profile=im.info.get("icc_profile"))

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
    item_url = urllib.parse.urlparse(entry[ITEM_URL_COL])
    item_id = item_url.path.split("/")[-1]
    entry["item_id"] = item_id
    entry["img_url"] = img_url
    if img_url.strip() == "imagem do computador" or "drive.google.com" in img_url:
        errors_list.append("Imagem indisponível na wikimedia e armazenada no Drive")

    # esses são erros que impedem o processamento da imagem já que não podemos baixá-la
    if errors_list:
        return entry, errors_list, True

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
            if len(coord) != 4:
                errors_list.append(
                    f"Categoria {caption} com área de corte com mais de 4 pontos."
                )
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

    return entry, errors_list, False


@command_line_entrypoint.command("bbox")
@click.argument("filename", type=click.Path(exists=True))
def crop_bboxes(filename):
    analisys = rows.import_from_csv(filename)
    for i, row in enumerate(analisys):
        entry, errors, skip_row = clean_row(row)
        if errors:
            print(f"{entry['item_id']} - ERRO - linha {i + 2}:")
            print("\t" + "\n\t".join(errors))
            if skip_row:
                continue
        try:
            image_path = download_image(entry["item_id"], entry["img_url"])
            process_image(entry, image_path)
        except UnidentifiedImageError:
            print(f"{entry['item_id']} - ERRO - linha {i + 2}:")
            print("\tFalha ao tentar baixar a imagem")


if __name__ == "__main__":
    command_line_entrypoint()
