#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pylint: disable=missing-docstring,no-self-use,wrong-import-order,wrong-import-position,invalid-name

import sys
from glob import glob

import polib

original_file = 'resources/language/resource.language.en_gb/strings.po'
original = polib.pofile(original_file, wrapwidth=0)

for translated_file in glob('resources/language/resource.language.*/strings.po'):

    # Skip original file
    if translated_file == original_file:
        continue

    print('Updating %s...' % translated_file)

    # Load po-files
    translated = polib.pofile(translated_file, wrapwidth=0)

    for entry in original:
        # Find a translation
        translation = translated.find(entry.msgctxt, 'msgctxt')

        if translation and entry.msgid == translation.msgid:
            entry.msgstr = translation.msgstr

    original.metadata = translated.metadata

    if sys.platform.startswith('win'):
        # On Windows save the file keeping the Linux return character
        with open(translated_file, 'wb') as _file:
            content = str(original).encode('utf-8')
            content = content.replace(b'\r\n', b'\n')
            _file.write(content)
    else:
        # Save it now over the translation
        original.save(translated_file)
