# -*- coding: utf-8 -*
import logging

import numpy as np
from osgeo import gdal

from composite_algorithm import Compositor

gdal.AllRegister()
gdal.UseExceptions()

logger = logging.getLogger(__name__)


class NDVIComposite(Compositor):
    """ Maximum NDVI composite """

    _red = 3
    _nir = 4
    _ndv = -9999

    input_info = ['_red', '_nir', '_ndv']
    input_info_str = ['Red Band Number',
                      'NIR Band Number',
                      'NoDataValue']
    description = 'Maximum NDVI composite'

    def __repr__(self):
        return "Maximum NDVI composite"

    def process_image(self, ncpu=1):
        """ Run compositing algorithm on entire image

        Args:
          ncpu (int, optional): number of CPUs to use - determines how to
            process into chunks

        """
        return

    def process_chunk(self, xoff, yoff, xsize, ysize):
        """ Process a chunk of an image

        Args:
          xoff (int): x offset
          yoff (int): y offset
          xsize (int): number of columns to process
          ysize (int): number of rows to process

        """
        return
