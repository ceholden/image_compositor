# -*- coding: utf-8 -*
import logging

import numpy as np
from osgeo import gdal

from composite_algorithm import Compositor

gdal.AllRegister()
gdal.UseExceptions()

logger = logging.getLogger(__name__)


class ZZCompositor(Compositor):
    """ Composite algorithm developed by Zhu Zhe """

    _blue = 1
    _nir = 4

    input_info = ['_blue', '_nir']
    input_info_str = ['Blue Band Number',
                      'NIR Band Number']
    description = 'Composite Algorithm by Zhu Zhe'

    def __repr__(self):
        return "Composite algorithm by Zhu Zhe"

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
