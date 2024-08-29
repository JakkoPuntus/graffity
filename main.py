from PIL import Image
import numpy as np
import zipfile
import os
import argparse


def quantize_image(image_path, num_colors=5):
    # Image loading
    image = Image.open(image_path)
    
    # Converting image to RGB
    image = image.convert('RGB')
    
    # Quantization of the image
    quantized_image = image.quantize(colors=num_colors, method=Image.MEDIANCUT)
    
    # Converting quantized image to numpy array
    quantized_np = np.array(quantized_image)
    
    return quantized_np, quantized_image.getpalette()

def create_color_layers(quantized_np, palette, num_colors=5):
    layers = []
    
    # Extracting RGB values from the palette
    palette_rgb = [palette[i:i+3] for i in range(0, len(palette), 3)]
    
    for i in range(num_colors):
        # Creating mask for the i-th color
        mask = (quantized_np == i)
        
        # Creating layer for the i-th color
        layer = np.zeros((*quantized_np.shape, 3), dtype=np.uint8)
        layer[mask] = palette_rgb[i]
        
        layers.append(layer)
    
    return layers

def save_layers(layers, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    layer_paths = []
    
    for i, layer in enumerate(layers):
        layer_image = Image.fromarray(layer)
        layer_path = os.path.join(output_dir, f'layer_{i+1}.png')
        layer_image.save(layer_path)
        layer_paths.append(layer_path)
    
    return layer_paths

def archive_layers(layer_paths, archive_name='layers.zip'):
    with zipfile.ZipFile(archive_name, 'w') as archive:
        for layer_path in layer_paths:
            archive.write(layer_path, os.path.basename(layer_path))
            os.remove(layer_path)

def create_graffiti_template(image_path, num_colors=5, output_dir='layers'):
    quantized_np, palette = quantize_image(image_path, num_colors)
    layers = create_color_layers(quantized_np, palette, num_colors)
    layer_paths = save_layers(layers, output_dir)
    archive_layers(layer_paths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create graffiti template from image')
    parser.add_argument('image_path', type=str, help='Path to the image')
    parser.add_argument('--num_colors', type=int, default=5, help='Number of colors in the template')
    parser.add_argument('--output_dir', type=str, default='layers', help='Output directory for layers')
    args = parser.parse_args()
    
    create_graffiti_template(args.image_path, args.num_colors, args.output_dir)