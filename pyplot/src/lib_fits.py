# -*- coding: utf-8 -*-
from npac import args
from astropy.io import fits


def init():
    """
    Check if the image name is correct or not.
    If not, ask it again.
    """
    global file_name
    global interactive

    # Allowed names for file_name
    names = ["common", "specific", "global"]

    try: # check if file_name exists as given by user
        file_name, interactive = args.get_args()
    except FileNotFoundError: # user can correct if previously wrong
        print('Files does not exist, file_name should be in : {}'.format(names))
        file_name = input('Enter file_name : \n')
        file_name = '../data/' + file_name + '.fits'
        interactive = input('Interactive mode [True/False] \n') # adjustment needed to define interactive without calling get_args()
        if interactive == 'True':
            interactive = True
        else :
            interactive = False
    return(file_name, interactive)

def read_first_image(file_name):
    """
    Return header and pixels of a .fits file_name.
    """
    pixels = None
    try : # open file_name
        with fits.open(file_name) as fits_blocks:
            block = fits_blocks[0]
            pixels = block.data
            header = block.header
    except IOError:
        print("Error while opening/reading file !")
        exit()
    except FileNotFoundError:
        print("Error with file name")
        exit()


    return header, pixels