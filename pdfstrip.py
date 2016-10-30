#!/usr/bin/env python3
#
# pdfstrip.py - strip objects from PDF files by specifying objects IDs
#
# Copyright (C) 2016  Antonio Ospite <ao2@ao2.it>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging
import sys

from pdfrw import PdfReader, PdfWriter
from pdfrw.objects.pdfindirect import PdfIndirect


# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(funcName)s:%(lineno)d %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.propagate = False


def strip_objects(pdf, objects_ids):
    for i, page in enumerate(pdf.pages):
        logger.debug("Page %d", i + 1)

        # Map all the objects in the page using the objects id as the key and
        # the resource name as the value.
        name_map = {indirect_obj.indirect[0]: name for name, indirect_obj in page.Resources.XObject.items()}
        logger.debug("name_map: %s", name_map)

        logger.debug("Before %s", page.Resources.XObject.keys())

        for obj in objects_ids:
            if obj in name_map:
                del page.Resources.XObject[name_map[obj]]

        logger.debug("After  %s\n", page.Resources.XObject.keys())

    return pdf


def validate_objects_ids(objects_ids_string):
    try:
        objects_ids = [int(obj) for obj in objects_ids_string.split(',')]
    except (IndexError, ValueError):
        raise argparse.ArgumentTypeError("%s contains an invalid value" % objects_ids_string)

    return objects_ids


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_filename",
                        help="the input PDF file (better if uncompressed)")
    parser.add_argument("output_filename",
                        help="the output PDF file")
    parser.add_argument("objects_ids",
                        type=validate_objects_ids,
                        help="a comma-separated list of objects IDs")
    parser.add_argument("-d", "--debug", action="store_true",
                        help="enable debug output")
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    pdf_data = PdfReader(args.input_filename)

    pdf_data = strip_objects(pdf_data, args.objects_ids)

    PdfWriter().write(args.output_filename, pdf_data)

    return 0


if __name__ == '__main__':
    sys.exit(main())
