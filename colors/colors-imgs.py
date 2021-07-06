import os
import tqdm
from pathlib import Path
import color_extraction
import matplotlib
import matplotlib.pyplot

DIR = 'fauna'

if __name__ == "__main__":
    source_dir = Path("fauna")
    images = [i for i in source_dir.iterdir() if ".jpg" == i.suffix]
    for image_path in tqdm.tqdm(images):
        out_dir = source_dir / 'rgb' / image_path.name.replace('.jpg', '')
        if not out_dir.exists():
            os.mkdir(out_dir)

        with matplotlib.cbook.get_sample_data(image_path.resolve()) as image_file:
            img = matplotlib.pyplot.imread(image_file)

        dict_rgb_arrays = color_extraction.get_rgb_arrays(img, median_filter=True)
        for color in dict_rgb_arrays:
            out_img = out_dir / (color + ".jpg")
            matplotlib.image.imsave(out_img.resolve(), dict_rgb_arrays[color])
