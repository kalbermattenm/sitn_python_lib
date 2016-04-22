# -*- coding: UTF-8 -*-
"""
FileName: tab2tfw.py
=============================================================================
Convert MapInfo Raster TAB to World files (TFW or EWW)
=============================================================================

Created: [2016/04/22]
Author: Michael Kalbermatten

"""

import math
import os
import sys
import logging
from argparse import ArgumentParser

def tab2tfw(args):
    FORMAT = "%(levelname)s: %(message)s"
    logging.basicConfig(level=args.loglevel or logging.INFO, format=FORMAT)

    _type = args.output_type.lower()
    if _type not in ('tfw','eww'):
        logging.info('Cannot create output "%s", please choose between tfw and eww' % _type)
        sys.exit(1)

    input_file = args.input_file

    if input_file is False:
        logging.debug('PAF')
        logging.info('No input file specified, please run script with -i defined')
        sys.exit(1)

    filename = os.path.basename(input_file).split('.')[0]
    logging.debug('Filename: %s' % filename)
    path2file = os.path.split(input_file)

    f = open(input_file)
    content = f.read()
    f.close()

    lines = content.split('\n')

    world_coord_lst = []
    pixel_coord_lst = []

    for line in lines:

        if line.find('Type') != -1:
            if line.find('RASTER') == -1:
                logging.info('TAB does not reference a raster data, stopping')
                sys.exit(1)

        if line.find('Label') != -1:
            world_coords_str = line.split(")")[0]
            world_coords_str = world_coords_str.split("(")
            world_coords_str = world_coords_str[len(world_coords_str)-1]
            world_coords_str = world_coords_str.split(',')
            idx = 0
            for val in world_coords_str:
                world_coords_str[idx] = float(val)
                idx += 1
            world_coord_lst.append(world_coords_str)
            pixel_coords_str = line.split("(")
            pixel_coords_str = pixel_coords_str[len(pixel_coords_str)-1]
            pixel_coords_str = pixel_coords_str.split(")")[0].split(',')
            idx = 0
            for val in pixel_coords_str:
                pixel_coords_str[idx] = float(val)
                idx += 1
            pixel_coord_lst.append(pixel_coords_str)

    if len(pixel_coord_lst) <2  or len(world_coord_lst) <2:
        logging.info("TAB file doesn't contain enough (or any?) coordinates, resolution calculations impossible, stopping !")
        sys.exit(1)

    r_xk_wad = math.pow((world_coord_lst[1][0] - world_coord_lst[0][0]), 2)
    r_yk_wad = math.pow((world_coord_lst[1][1] - world_coord_lst[0][1]), 2)
    num_real_dist = math.sqrt(r_xk_wad+r_yk_wad)
    logging.debug('Real distance: %s' % num_real_dist)

    p_xk_wad = math.pow((pixel_coord_lst[1][0] - pixel_coord_lst[0][0]), 2)
    p_yk_wad = math.pow((pixel_coord_lst[1][1] - pixel_coord_lst[0][1]), 2)
    num_pixel_dist = math.sqrt(p_xk_wad + p_yk_wad)
    logging.debug('Pixel distance: %s' % num_pixel_dist)
      
    resolution = (num_real_dist/num_pixel_dist)
    logging.debug('Resolution: %s' % resolution)

    x_shift = world_coord_lst[0][0] - (pixel_coord_lst[0][0] * resolution)
    y_shift = world_coord_lst[0][1] + (pixel_coord_lst[0][1] * resolution)

    x_shift = x_shift + (resolution / 2)
    y_shift = y_shift - (resolution / 2)

    if _type == 'tfw':
        filename += '.tfw'
    elif _type == 'eww':
        filename += '.eww'

    filename = os.path.join(path2file[0], filename)
    logging.debug('Output file: %s' % filename)
    f = open(filename, 'w')

    f.write("%0.10f" % (resolution) + "\n")
    f.write("0\n")
    f.write("0\n")
    f.write("-%0.10f" % (resolution) + "\n")
    f.write("%0.4f" % (x_shift) + "\n")
    f.write("%0.4f" % (y_shift) + "\n") 

    f.close()
    sys.exit(0)

if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--verbose', help='Verbose (debug) logging', action='store_const', const=logging.DEBUG,
                       dest='loglevel')
    parser.add_argument('-i', '--input-file', help='Path to TAB input file (required)', action='store')
    parser.add_argument('-o', '--output-type', help='Specify if output is TFW (default) or EWW', action='store', default='tfw')

    args = parser.parse_args()

    tab2tfw(args)
