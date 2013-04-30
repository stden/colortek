# coding: utf-8
# Works with csv input steam with help of general csv library builtin in python
# requirements: python 2.6+
import os
import zipfile
# settings file
from django.conf import settings
import Image
from cStringIO import StringIO

IMAGE_SAVE_PATH = 'items/%s/%s'
def save_item_image(upfile, item, path):
    """ saves picture in constant path, getting parameter what file form
    zipfile need to save"""

    if not upfile:
        return ''
    zp = zipfile.ZipFile(upfile)
    filepath = ''
    if path in zp.namelist():
        idx = zp.namelist().index(path)
        uncompressed = zp.open(zp.filelist[idx], 'r')
        buf = StringIO(uncompressed.read())
        try:
            image = Image.open(buf)
        except IOError:
            return ''
        filename = path.split('/')[-1]
        rel_file_path = IMAGE_SAVE_PATH % (item.container.id, '%s_%s' % (item.pk, filename))
        filepath = os.path.join(
            settings.MEDIA_ROOT,
            rel_file_path
        )

        try:
            os.makedirs(filepath[:filepath.rindex('/')])
        except OSError:
            pass

        image.save(
            os.path.join(
                settings.MEDIA_ROOT,
                filepath,
            )
        )
    return rel_file_path
