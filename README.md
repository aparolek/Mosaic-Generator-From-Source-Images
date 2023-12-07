# Mosaic-Generator-From-Source-Images
Using the "final_output" function, and specifying an image directory, you can create a mosaic. The mosaic will be made out of all images inside the source folder.
You have to specify a pp value which reperesents the pixels per source image. A lower pp means that the image will be of greater quality, but will take alot longer to process.

Within the "final_output" function the two varialbe src_image_width, src_image_height, say how large a source image will be in terms of pixels. The code will reformat all the source images to be of this size. It is automatically set to 125 as this makes the original images to still be visible while not taking too much time to process.

There is currently no error handling at all. A known error is using a low value for large images, the recursive image function hits the recursive depth.

# PREREQUISITES
- Pillow
- opencv
- numpy
- time
