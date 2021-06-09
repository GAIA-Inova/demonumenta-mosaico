#!/usr/bin/env python3
import click
import rows
from PIL import UnidentifiedImageError

import csv_parser


@click.group()
def command_line_entrypoint():
    """
    Ferramenta pra explorar imagens do dataset Open Images V6
    """
    pass


@command_line_entrypoint.command("bbox")
@click.argument("filename", type=click.Path(exists=True))
def crop_bboxes(filename):
    analisys = rows.import_from_csv(filename)
    for i, row in enumerate(analisys):
        entry, errors, skip_row = csv_parser.clean_row(row)
        if errors:
            print(f"{entry['item_id']} - ERRO - linha {i + 2} por {entry['seu_email']}:")
            print("\t" + "\n\t".join(errors))
            if skip_row:
                continue
        try:
            image_path = csv_parser.download_image(entry["item_id"], entry["img_url"], from_local=entry.get('local_file'))
            csv_parser.process_image(entry, image_path)
        except UnidentifiedImageError:
            print(f"{entry['item_id']} - ERRO - linha {i + 2} por {entry['seu_email']}:")
            print("\tFalha ao tentar baixar a imagem")
        except csv_parser.UnexistingImageException as e:
            print(f"{entry['item_id']} - ERRO - linha {i + 2} por {entry['seu_email']}:")
            print(f"\t{e}")

if __name__ == "__main__":
    command_line_entrypoint()
