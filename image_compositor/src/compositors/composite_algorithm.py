# -*- coding: utf-8 -*

import abc
import logging

import numpy as np
from osgeo import gdal

gdal.AllRegister()
gdal.UseExceptions()

logger = logging.getLogger(__name__)


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

    @abc.abstractproperty
    def description(self):
        return

    @abc.abstractproperty
    def input_info(self):
        return

    @abc.abstractproperty
    def input_info_str(self):
        return

    def _get_image_attributes(self, image):
        """ Return image attributes useful for validation

        Args:
          image (str): filename of image

        Returns:
          attributes (tuple): tuple of projection, pixel sizes, UL x and y
            posting, and the number of bands

        """
        ds = gdal.Open(image, gdal.GA_ReadOnly)
        proj = ds.GetProjection()

        gt = ds.GetGeoTransform()
        # Only deal with north-up images for right now
        if gt[2] != 0 or gt[4] != 0:
            logger.warning('Only supporting north-up images for now')
            raise ValueError('Only can use north-up images')

        px_size, py_size = gt[1], gt[5]
        ul_x, ul_y = gt[0], gt[3]

        nband = ds.RasterCount

        return (proj, px_size, py_size, ul_x, ul_y, nband)

    def validate_images(self, images):
        """ Validates which images in self.files can be used for composites

        The default compositing algorithm implementation will not perform
        any resampling or reprojections.

        Thus, the default validation ensures all images have:
            - common projection
            - common pixel size
            - common pixel postings (e.g., offset by whole number of pixels)
            - common number of bands

        Args:
          images (list): list of filenames for images to be validated

        Returns:
          valid (list): True or False for each file in self.file if file is
            usable within the algorithm

        """
        valid = []
        # Get attributes from first image
        for image in images:
            try:
                self.proj, \
                    self.px_size, self.py_size, \
                    self.ul_x, self.ul_y, \
                    self.nband = \
                    self._get_image_attributes(images)
            except ValueError:
                valid.append(False)
            else:
                valid.append(True)
                break

        for image in images[len(valid):]:
            _valid = True

            _proj, _px, _py, _ul_x, _ul_y, _nband = \
                self._get_image_attributes(image)

            if _proj != self.proj:
                logger.warning('Image {i} has different projection than base \
                    image'.format(i=image))
                _valid = False

            if _px != self.px_size or _py != self.py_size:
                logger.warning('Image {i} has different pixel size than base \
                    image'.format(i=image))
                _valid = False

            if (self.ul_x - _ul_x) % self.px_size != 0 or \
                    (self.ul_y - _ul_y) % self.py_size != 0:
                logger.warning('Image {i} has different posting than base\
                    image'.format(i=image))
                _valid = False

            if _nband != self.nband:
                logger.warning('Image {i} has different number of bands than \
                    base image'.format(i=image))
                _valid = False

            valid.append(_valid)

        return valid

    def process_image(self, ncpu=1):
        """ Run compositing algorithm on entire image

        Args:
          ncpu (int, optional): number of CPUs to use - determines how to
            process into chunks

        """
        logger.debug('Running algorithm')
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
