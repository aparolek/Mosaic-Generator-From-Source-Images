from glob import glob
import os
from PIL import Image, ImageOps
import math 
import os.path
import numpy as np
import cv2
import time

src_dir = r"source"
img_dir = input("Input Image Directory: ")

source_dict = {}

src_images = {} # used to store source image objects for each image to avoid reloading from disk

pixel_to_src_img = {} # storing a local cache of rgb to source image again to stop from reloading from disk

def average_colours(colours) -> tuple:
        reds = []; greens = []; blues = []

        for colour in colours:
                for i in range(0, colour[0]):
                        reds.append(colour[1][0])
                        greens.append(colour[1][1])
                        blues.append(colour[1][2])

        return (
                sum(reds)//len(reds),
                sum(greens)//len(greens),
                sum(blues)//len(blues)
        )

def average_colours2(colours) -> tuple:
        reds = []; greens = []; blues = []

        for colour in colours:
                reds.append(colour[0])
                greens.append(colour[1])
                blues.append(colour[2])

        return (
                sum(reds)//len(reds),
                sum(greens)//len(greens),
                sum(blues)//len(blues)
        )

def distance_between_vector(a,b):
        # where a and b are 2 3D vectors
        x = a[0]-b[0]
        y = a[1]-b[1]
        z = a[2]-b[2]
        dist_squared = x**2 + y**2 + z**2
        distance = math.sqrt(dist_squared)
        #returns distance between two vectors
        return distance

def closest_img(pixel):
        global pixel_to_src_img
        try:
                return pixel_to_src_img[pixel]
                # checks if entry is in dictionary
        except KeyError:
                #key value error will occur when it is not found in the dictionary
                current_distance = 441
                #441 is the largest distance possible


                for img in source_dict:
                        if distance_between_vector(pixel,source_dict[img]) < current_distance:
                                #when smallest distan
                                current_distance = distance_between_vector(pixel,source_dict[img])
                                final = img
                pixel_to_src_img[pixel] = final
                #we add to the global dictonary
                return final

def pixel_mapping(pp):
    #pixels per blocks is the length and width that each block takes
    img = Image.open(img_dir)
    img = img.convert("RGB")
    image_width, image_height = img.size

    #size of the image may not be perfectly devisible by the block sizes so we
    resize_height = (image_height//pp) * pp
    resize_width = (image_width//pp) * pp 
    img.resize((resize_width, resize_height))
    #resize so that the image is can be broken down by our squares
    rgb_im = img.convert('RGB')

    pixel_map = []
    #creating empty map
    for i in range (0 , resize_height//pp):
        pixel_map.append([])
        for j in range(0 ,resize_width//pp):
                pixel_map[i].append([])
    #filling the map in accordingly
    for i in range (0 , resize_height):
        for j in range(0 ,resize_width):
                r, g, b = rgb_im.getpixel((j, i))
                pixel = (r,g,b)
                pixel_map[i//pp][j//pp].append(pixel)
    return pixel_map #pixel mapping is a 3D array


def add_image_hrzntl(image1, image2): #concatinates first image to second and returns image OBJECT
    image1_width, image1_height = image1.size
    image2_width, image2_height = image2.size
    new_image = Image.new('RGB',(image1_width+image2_width, image1_height), (250,250,250))
    new_image.paste(image1,(0,0))
    new_image.paste(image2,(image1_width,0))
    return new_image
   
#RECURSIVE FUNCTION
def createlines(listline):
        global src_images
        try:
                # Check if the image is in the src_images in cache before loading from disk
                tile_image = src_images[listline[0]]
        except KeyError:
                tile_image = Image.open(listline[0])
                src_images[listline[0]] = tile_image # Add image to src_images cache

        finally:
                #basecase, when the list == 1 it will finish
                if len(listline) == 1:
                        return tile_image
                else:
                        return add_image_hrzntl(createlines(listline[1:]) , tile_image)


def final_output(pp): #referse to pixel are asigned per source image
        src_image_width, src_image_height = 125, 125
        #size the source image will be in the final image, lower values will increase perfomance alot
        #WARNING, permanently changing these values will permanently reformat images, do not use too low of values

        dir_path = src_dir + "/"
        print("\nImages Being Used:")
        for file_path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file_path)):
                print("   " + file_path)
                img = cv2.imread(dir_path + file_path, cv2.IMREAD_UNCHANGED)
                dim = (src_image_width, src_image_height)
                resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
                os.remove(dir_path + file_path)
                cv2.imwrite(dir_path + file_path[:-4] + ".jpg", resized) 


        #fills dictionary with average colour of each source image
        for filename in os.scandir(src_dir):
                if filename.is_file():
                        #print(filename.path)
                        src_image = Image.open(filename.path)

                        colours = src_image.convert('RGB').getcolors(src_image.size[0]*src_image.size[1])

                        avgcolour = average_colours(colours)

                        source_dict.update({filename.path: avgcolour})

        pixel_map = pixel_mapping(pp)
        src_array = []
        count = -1
        for i in pixel_map:
                src_array.append([])
                count += 1
                for j in i:
                        src_array[count].append(closest_img(average_colours2(j)))

        output = Image.new("RGB", (src_image_width*len(src_array[0]), src_image_height*len(src_array)), "white")
        count = 0
        for line in src_array:
                im_mirror = ImageOps.mirror(createlines(line))
                line_width, line_height = im_mirror.size        
                output.paste(im_mirror, (0, line_height*count))
                count += 1
        output.save("output.jpg")


pp = int(input("\nEnter PP: "))

# PP represents how many pixels a single source image will represent, lower value will make a higher res image but 
# performance will take a big hit
#use number > 10 for faster times

start = time.time()
final_output(pp)
end = time.time()

print(f"\nComplete! Processed In: {end - start}")
