import cv2
import hashlib
import imghdr
import numpy as np
import os
from PIL import Image, ImageDraw
from random import randint


def file_as_bytes(file):
    '''read image file as bytes'''
    with file:
        return file.read()


def hash_file(fpath):
    '''create hash file'''
    return hashlib.md5(file_as_bytes(open(fpath, 'rb'))).hexdigest()



def rename_files(fpath, unique_images):
    # separating the directory path (head) from the file (tail)
    head, tail = os.path.split(fpath)
    # separating the name of the file from its extension
    name, ext = os.path.splitext(tail)
    # find correct file extension 
    ext = '.' + imghdr.what(fpath)
    # getting md5sum for image file
    hash = hash_file(fpath)
    # joining file hash with file extension
    hash_name = hash + ext
    #checking for duplicate files
    if hash_name not in unique_images:
        unique_images.append(hash_name)
        # rename file as file hash + ext 
        os.rename(fpath, os.path.join(head, hash_name))
        print(os.path.join(head, hash_name))
    else:
        os.remove(fpath)                      # remove the duplicates

    return os.path.join(head, hash_name)


def image_resize(image_file):
    ''' Check image width and height. If width or/and height are bigger than 
    1080 pixels, image is resized. Biggest dimension will be 1080 pixels and 
    the other dimension is altered not affecting the aspect ratio'''

    img=Image.open(image_file)
    # img.size is a tuple (width,height)
    img_width = img.size[0]
    img_height = img.size[1]

    maxwidth = 1080    # desired max width
    maxheight = 1080   # desired max height

    # width is bigger than maxwidth and it is the biggest dimension on the image or it is a square image
    if img_width > maxwidth and img_width >= img_height:
        wratio = (maxwidth/float(img_width))
        hsize = int((float(img_height))*(float(wratio)))
        img = img.resize((maxwidth,hsize), Image.ANTIALIAS)
        img.save(image_file)

    # height is bigger than maxheight and it is the biggest dimension on the image
    elif img_height > maxheight and img_height > img_width:
        hratio = (maxheight/float(img_height))
        wsize = int((float(img_width))*(float(hratio)))
        img = img.resize((wsize,maxheight), Image.ANTIALIAS)
        img.save(image_file)


def is_transparent(image_filepath):
    img = Image.open(image_filepath)
    if img.mode == 'RGBA' or 'transparency' in img.info:
        return True
    elif imghdr.what(image_filepath) == ['png','gif']:
        return True
    else:
        return False




def append_background(infile, inbg):
    """ Function to paste background to an image and save it
    INPUT: original image, background image
    OUTPUT: image rendered
    """

    try:  # Check if the files are images
        print(infile)
        img = Image.open(infile).convert('RGBA')
        bg = Image.open(inbg).convert('RGBA')
        width, height = img.size
        bgWidth, bgHeight = bg.size
        print("background appended!")
    except:
        print("File is not an image.")
        return
    # Get aspect ratios of the input and background images
    aspectRatio = width / height
    bgAspectRatio = bgWidth / bgHeight
    if (aspectRatio > bgAspectRatio):  # input image is wider
        # Resize BG such that BG width = input image width
        newBgWidth = width
        newBgHeight = int(newBgWidth * bgHeight / bgWidth)
        bg = bg.resize((newBgWidth, newBgHeight), Image.ANTIALIAS)
        # Paste input image to BG, center-aligned
        bg.paste(img, (0, int((newBgHeight / 2) - (height / 2))), img)
        # Crop image to retain input image dimensions
        bg = bg.crop((0, int((newBgHeight / 2) - (height / 2)),
                     width, int((newBgHeight / 2) + (height / 2))))
    else:  # background is wider
        # Resize BG such that BG width = input image width
        newBgHeight = height
        newBgWidth = int(newBgHeight * bgWidth / bgHeight)
        bg = bg.resize((newBgWidth, newBgHeight), Image.ANTIALIAS)
        # Paste input image to BG, center-aligned
        bg.paste(img, (int((newBgWidth / 2) - (width / 2)), 0), img)
        # Crop image to retain input image dimensions
        bg = bg.crop((int((newBgWidth / 2) - (width / 2)), 0,
                     int((newBgWidth / 2) + (width / 2)), height))
    # Save resulting image to output folder, located in the same directory/file
    # name as oriented in the input folder
    bg.save(infile, "PNG")




blacklist = {
    'aerosol_cans_full': ['carpet'],
    'aluminium_foil': [],
    'ammunition': [],
    'auto_parts': ['greenery'],
    'batteries': ['abstract'],
    'bicycles': ['inside_car', 'tabletop'],
    'cables': [],
    'cardboard': [],
    'cartridge': [],
    'cassette': [],
    'cd_cases': [],
    'cigarettes': ['carpet'],
    'cooking_oil': ['greenery', 'carpet', 'inside_car', 'urban_outdoor'],
    'cookware': ['greenery', 'carpet', 'inside_car', 'garage', 'urban_outdoor'],
    'corks': ['inside_car'],
    'crayons': [],
    'digital_cameras': [],
    'desktop_computers': ['greenery'],
    'discs': ['abstract'],
    'doors': ['inside_car'],
    'eyeglasses': ['abstract'],
    'fabrics': ['urban_outdoor'],
    'fire_extinguishers': ['urban_outdoor', 'greenery', 'inside_car'],
    'floppy_disks': [],
    'furniture': ['inside_car'],
    'game_consoles': [],
    'generic_plastic': ['abstract'],
    'gift_bags': [],
    'glass': ['abstract', 'inside_car'],
    'glass_container': ['abstract'],
    'green_waste': ['abstract', 'inside_car', 'carpet'],
    'hard_drives': [],
    'hardware': ['abstract'],
    'hazardous_fluid': ['carpet', 'abstract'],
    'heaters': ['inside_car'],
    'laptop_computers': [],
    'large_appliance': ['inside_car', 'tabletop'],
    'lightbulb': ['abstract'],
    'medication_containers': ['abstract'],
    'medications': [],
    'metal_cans': [],
    'mixed_paper': ['abstract'],
    'mobile_device': [],
    'monitors': [],
    'nail_polish': [],
    'oil_filters': ['carpet'],
    'paint': ['abstract'],
    'paint_thinner': [],
    'pallets': ['carpet', 'tabletop', 'inside_car'],
    'paper_cups': [],
    'pet_waste': ['carpet', 'hardwood', 'tabletop', 'abstract'],
    'plastic_cards': [],
    'printers': [],
    'propane_tanks': [],
    'shoes': [],
    'small_appliances': ['abstract'],
    'smoke_detectors': [],
    'tires': ['tabletop', 'carpet', 'abstract'],
    'tools': ['abstract'],
    'toothbrushes': [],
    'toothpaste_tubes': [],
    'toy': [],
    'vehicles': ['inside_car', 'carpet', 'tabletop'],
    'water_filters': [],
    'wood': ['carpet'],
    'wrapper': ['abstract'],
    }

def update_classes(class_file, texts):
    response = input(f"Perform update check with '{class_file}'? (y/n) ")
    while response not in ['y','n']:
        response = input("invalid response, (y,n): ")
    if response == 'n':
        return
    if response == 'y':
        print("Checking classes...")

    classes_dict = {} # dictionary mapping items in classes.txt to line number
    with open(class_file,'r') as f:
        for i, line in enumerate(f):
            classes_dict.update({line.rstrip() : str(i+1)})

    # Check for changes in each line of each file
    changes = 0 # keep track of number of files changed
    for text in texts:
        current_class = text.split('/')[-2]
        try:
            new_class_num = classes_dict[current_class]
        except KeyError: # Stops operation if a class has been deleted
            print(f"{'-'*50}\nclass '{current_class}' doesn't exist in '{class_file}'\n \
                manually remove or delete it from images directory and try again")
            exit(1)

        with open(text,'r+') as t:
            # convert each line into a list
            # modify the number if necessary
            lines = [line for line in t]
            for i, line in enumerate(lines):
                #print(line.split(',')[0]) # first number
                #print(new_class_num)
                if line.split(',')[0] != new_class_num:
                    changes += 1
                    print(f"changing class label for '{text}' \
                        \nfrom {line.split(',')[0]} to {new_class_num}")
                    lines[i] =  f"{new_class_num},{','.join(line.split(',')[1:])}"

            t.seek(0) # go to zeroth byte in file, fully overwrite, truncate
            t.write(''.join(lines))
            t.truncate()


    if changes > 0:
        print(f"i\nnumber of files changes made: {changes}")
    else: 
        print("\nno changes made to class labels")
