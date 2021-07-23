from pathlib import Path

DEMONUMENTA_ROOT = Path("/home/bernardo/envs/demonumenta/demonumenta")
IMAGES_DIR = DEMONUMENTA_ROOT / "imagens"
MOSAIC_DIR = DEMONUMENTA_ROOT / "mosaico"
CAPTIONS_DIR = DEMONUMENTA_ROOT / "captions"
OFFLINE_IMGS_DIR = DEMONUMENTA_ROOT / "AAA_Extras"
SPLIT_TOKEN = "&"

CAPTIONS = {
    "flora": "Flora",
    "homem_branco": "Homem Branco",
    "ceu": "Céu",
    "mulher_branca": "Mulher Branca",
    "homem_negro": "Homem Negro",
    "mulher_negra": "Mulher Negra",
    "homem_indigena": "Homem Indígena",
    "mulher_indigena": "Mulher Indígena",
    "crianca_branca": "Criança Branca",
    "crianca_branca_f": "Criança Branca (F)",
    "crianca_negra": "Criança Negra",
    "crianca_negra_f": "Criança Negra (F)",
    "crianca_indigena": "Criança Indígena",
    "crianca_indigena_f": "Criança Indígena (F)",
    "bandeirante": "Bandeirante",
    "figura_religiosa": "Figura Religiosa",
    "igreja": "Igreja",
    "artefatos_exteriores_ferramentas_de_trabalho_adornos_etc": "Artefatos exteriores",
    "residencia_abastada": "Residência (abastada)",
    "cafeicultor": "Cafeicultor",
    "fazendeiro": "Fazendeiro",
    "politico": "Político",
    "militar": "Militar",
    "trabalhador_urbano": "Trabalhador urbano",
    "escravizado": "Escravizado",
    "ex_escravizado": "Ex-Escravizado",
    "industrial": "Industrial",
    "trabalhador_rural": "Trabalhador rural",
    "residencia_pobre": "Residência (pobre)",
    "espaco_cultural": "Espaço cultural",
    "espaco_administrativo_politico": "Espaço administrativo/ político",
    "ruas_e_pracas": "Ruas e praças",
    "artefatos_domesticos_mobiliario_utilitarios_adornos_etc": "Artefatos domésticos",
    "fauna": "Fauna",
}
CAPTIONS_REVERSE = {v: k for k, v in CAPTIONS.items()}

IMG_URL_COL = "link_do_arquivo_clique_no_link_da_planilha_e_copie_a_url_que_aparece_no_seu_browser_atencao_essa_url_termina_com_jpg"
ITEM_URL_COL = "link_do_identificador_label_copie_e_cole_a_url_que_aparece_na_coluna_da_esquerda_ex_http_www_wikidata_org_entity_q59924915_a_informacao_qxxxxxxxx_e_muito_importante"
