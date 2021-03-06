import os
from glob import glob

import numpy as np
from PIL import Image as Img
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.preprocessing.image import load_img

from .u2net_test import convert_file


def remove_image(image_name):
    # get the names of the images that were uploaded, removing .png
    convert_file(image_name)
    image_dir = os.path.join(os.getcwd(), 'results/*.png')
    file_names = glob(image_dir)
    # print(file_names)
    names = [os.path.basename(name[:-4]) for name in file_names]
    for name in names:
        return process_image_named(name)


def process_image_named(name, threshold_cutoff=0.90, use_transparency=True):
    path = os.path.join(os.getcwd(), 'results/' + name + '.png')
    result_img = load_img(path)
    # convert result-image to numpy array and rescale(255 for RBG images)
    RESCALE = 255
    out_img = img_to_array(result_img)
    out_img /= RESCALE
    # define the cutoff threshold below which, background will be removed.
    THRESHOLD = threshold_cutoff

    # refine the output
    out_img[out_img > THRESHOLD] = 1
    out_img[out_img <= THRESHOLD] = 0

    if use_transparency:
        # convert the rbg image to an rgba image and set the zero values to transparent
        shape = out_img.shape
        a_layer_init = np.ones(shape=(shape[0], shape[1], 1))
        mul_layer = np.expand_dims(out_img[:, :, 0], axis=2)
        a_layer = mul_layer * a_layer_init
        rgba_out = np.append(out_img, a_layer, axis=2)
        mask_img = Img.fromarray((rgba_out * RESCALE).astype('uint8'), 'RGBA')
    else:
        mask_img = Img.fromarray((out_img * RESCALE).astype('uint8'), 'RGB')

    # load and convert input to numpy array and rescale(255 for RBG images)
    input = load_img(os.path.join(os.getcwd(), 'media/' + name + '.jpg'))
    inp_img = img_to_array(input)
    inp_img /= RESCALE

    if use_transparency:
        # since the output image is rgba, convert this also to rgba, but with no transparency
        a_layer = np.ones(shape=(shape[0], shape[1], 1))
        rgba_inp = np.append(inp_img, a_layer, axis=2)

        # simply multiply the 2 rgba images to remove the backgound
        rem_back = (rgba_inp * rgba_out)
        rem_back_scaled = Img.fromarray((rem_back * RESCALE).astype('uint8'), 'RGBA')
    else:
        rem_back = (inp_img * out_img)
        rem_back_scaled = Img.fromarray((rem_back * RESCALE).astype('uint8'), 'RGB')

    # select a layer(can be 0,1 or 2) for bounding box creation and salient map
    LAYER = 2
    out_layer = out_img[:, :, LAYER]

    # find the list of points where saliency starts and ends for both axes
    x_starts = [
        np.where(out_layer[i] == 1)[0][0] if len(np.where(out_layer[i] == 1)[0]) != 0 else out_layer.shape[0] + 1 for i
        in range(out_layer.shape[0])]
    x_ends = [np.where(out_layer[i] == 1)[0][-1] if len(np.where(out_layer[i] == 1)[0]) != 0 else 0 for i in
              range(out_layer.shape[0])]
    y_starts = [
        np.where(out_layer.T[i] == 1)[0][0] if len(np.where(out_layer.T[i] == 1)[0]) != 0 else out_layer.T.shape[0] + 1
        for i in range(out_layer.T.shape[0])]
    y_ends = [np.where(out_layer.T[i] == 1)[0][-1] if len(np.where(out_layer.T[i] == 1)[0]) != 0 else 0 for i in
              range(out_layer.T.shape[0])]

    # get the starting and ending coordinated for the box
    startx = min(x_starts)
    endx = max(x_ends)
    starty = min(y_starts)
    endy = max(y_ends)

    # show the resulting coordinates
    start = (startx, starty)
    end = (endx, endy)
    start, end

    cropped_rem_back_scaled = rem_back_scaled.crop((startx, starty, endx, endy))
    if use_transparency:
        cropped_rem_back_scaled.save(os.path.join(os.getcwd(), 'media/' + name + '_cropped_no-bg.png'))
    else:
        cropped_rem_back_scaled.save(os.path.join(os.getcwd(), 'media/' + name + '_cropped_no-bg.jpg'))

    # cropped_mask_img = mask_img.crop((startx, starty, endx, endy))

    # if use_transparency:
    #     cropped_mask_img.save(os.path.join(os.getcwd(), 'cropped_results/' + name + '_cropped_no-bg_mask.png'))
    # else:
    #     cropped_mask_img.save(os.path.join(os.getcwd(), 'cropped_results/' + name + '_cropped_no-bg_mask.jpg'))
    if os.path.exists(path):
        # removing the file using the os.remove() method
        os.remove(path)
        print("File remove directory")
    else:
        # file not found message
        print("File not found in the directory")

    return 'media/' + name + '_cropped_no-bg.png'
