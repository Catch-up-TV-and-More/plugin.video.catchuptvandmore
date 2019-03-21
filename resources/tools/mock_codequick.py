# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import mock


mock_codequick = mock.MagicMock()


# Say to Python that the codequick module is mock_codequick
sys.modules['codequick'] = mock_codequick
