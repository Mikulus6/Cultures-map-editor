from PIL import Image, ImageDraw, ImageFont
from scripts.colormap import template_editgroups_palette

font_name = "verdana.ttf"
font_size = 11
# Out of all commonly accessible fonts, Verdana with size 11 seems to be the closest font
# to the one used in "Cultures - Northland" in file "Editor\Premaps\Misc\Palette.pcx".

file_name = "Palette.png"

palette_image = Image.new("RGB", (260, 15*(len(template_editgroups_palette) + 2)), (219, 219, 219))
palette_image_draw = ImageDraw.Draw(palette_image, mode=palette_image.mode)
palette_image_draw.fontmode = "1"

font = ImageFont.truetype(font_name, font_size)

for index, name in enumerate(template_editgroups_palette.keys()):

    palette_image_draw.rectangle((26, 15*(index+1), 98, 15*(index+2)),
                                 fill=template_editgroups_palette[name],
                                 outline=(0, 0, 0))
    palette_image_draw.text((112, 15*(index+1)), name, (0, 0, 0), font)

palette_image.save(file_name)
print("Palette was successfully created.")
