#!/usr/bin/env python3
import csv
import click
import rows
from tqdm import tqdm
from PIL import UnidentifiedImageError
from collections import OrderedDict, defaultdict

from constants import CAPTIONS, MOSAIC_DIR
import csv_parser
import tagging


@click.group()
def command_line_entrypoint():
    """
    Ferramenta para explorar imagens do Museu Paulista para o projeto Demonumenta
    """
    pass


@command_line_entrypoint.command("bbox")
@click.argument("filename", type=click.Path(exists=True))
def crop_bboxes(filename):
    analisys = rows.import_from_csv(filename)
    output_rows = []
    for i, row in enumerate(analisys):
        line = i + 2
        entry, errors, skip_row = csv_parser.clean_row(row)
        if errors:
            print(f"{entry['item_id']} - ERRO - linha {line} por {entry['seu_email']}:")
            print("\t" + "\n\t".join(errors))
            if skip_row:
                continue
        try:
            image_path = csv_parser.download_image(
                entry["item_id"], entry["img_url"], from_local=entry.get("local_file")
            )
            tags_result = csv_parser.process_image(entry, image_path)

            for caption, outputs in tags_result.items():
                for tag_img in outputs:
                    out_row = OrderedDict()
                    out_row["Categoria"] = CAPTIONS[caption]
                    out_row["Imagem"] = tag_img['image'].relative_to(MOSAIC_DIR / caption)
                    out_row["Área"] = ','.join([str(i) for i in tag_img['area']])
                    out_row["Item"] = entry["item_id"]
                    out_row["Suporte"] = entry["suporte"]
                    out_row["Num. Inventario"] = entry["numero_inventario"]
                    out_row["Tags"] = entry["tags"].strip()
                    out_row["Descrição"] = entry["descricao_utilze_esse_espaco_para_redigir_um_verbete_sobre_a_imagem_analisada"].strip()
                    out_row["Email"] = entry["seu_email"]
                    out_row["Item Url"] = f'https://www.wikidata.org/wiki/{entry["item_id"]}'
                    out_row["Img Url"] = entry["img_url"]
                    out_row["Linha Planilha Resposta"] = line

                    output_rows.append(out_row)
        except UnidentifiedImageError:
            print(f"{entry['item_id']} - ERRO - linha {line} por {entry['seu_email']}:")
            print("\tFalha ao tentar baixar a imagem")
        except csv_parser.UnexistingImageException as e:
            print(f"{entry['item_id']} - ERRO - linha {line} por {entry['seu_email']}:")
            print(f"\t{e}")

    with open('output.csv', 'w', newline='') as fd:
        writer = csv.DictWriter(fd, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)


@command_line_entrypoint.command("tag")
@click.argument("filename", type=click.Path(exists=True))
def crop_bboxes(filename):
    annotations = list(rows.import_from_csv(filename))
    rows_per_image = defaultdict(list)
    for i, row in enumerate(annotations, start=2):
        image_path = tagging.get_image_path(row.item)
        if not image_path.exists():
            print(f'Linha {i} com imagen faltando {row.item}')
        rows_per_image[row.item].append(row)

    for item, annotations in tqdm(list(rows_per_image.items())):
        tagging.tag_image(item, annotations)


if __name__ == "__main__":
    command_line_entrypoint()
