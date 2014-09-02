# -*- coding: utf-8 -*

import abc
import logging

import numpy as np
from osgeo import gdal

gdal.AllRegister()
gdal.UseExceptions()

logger = logging.getLogger('image_compositor')


class Compositor(object):
    """ Abstract base class for image compositors

    This class is meant to be subclassed and many of its methods overridden by
    specific algorithms. The structure presented here documents what each
    individual composite needs to be usable by command line applications or
    GUIs within this project.

    Attributes:
      files (list): list of filenames to be used in composite
      input_info (list): list of variables requiring user input
      input_info_str (list): associated labels for required user inputs

    Required methods:
      validate_images: method to validate suitability of images
      process_image: method to perform algorithm on entire image
      process_chunk: method to perform algorithm on an amount of data

    """

    __metaclass__ = abc.ABCMeta

    def __repr__(self):
        return "A compositing algorithm"

    def __init__(self, files):
        """ Initialize compositing algorithm with list of files

        Args:
          files (list): list of filenames to be used in composite

        """
        self.files = files

    @abc.abstractproperty
    def input_info(self):
        return

    @abc.abstractproperty
    def input_info_str(self):
        return

    def validate_images(self):
        """ Validates which images in self.files can be used for composites

        The default compositing algorithm implementation will not perform
        any resampling or reprojections.

        Thus, the default validation ensures all images have:
            - common projection
            - common pixel size
            - common pixel postings (e.g., offset by whole number of pixels)
            - common number of bands

        Returns:
          valid (list): True or False for each file in self.file if file is
            usable within the algorithm

        """
        # TODO
        return

    @abc.abstractmethod
    def process_image(self, ncpu=1):
        """ Run compositing algorithm on entire image

        Args:
          ncpu (int, optional): number of CPUs to use - determines how to
            process into chunks

        """
        return

    @abc.abstractmethod
    def process_chunk(self, xoff, yoff, xsize, ysize):
        """ Process a chunk of an image

        Args:
          xoff (int): x offset
          yoff (int): y offset
          xsize (int): number of columns to process
          ysize (int): number of rows to process

        """
        return
