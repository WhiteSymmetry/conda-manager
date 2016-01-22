# -*- coding:utf-8 -*-
#
# Copyright © 2015 The Spyder Development Team
# Copyright © 2014 Gonzalo Peña-Castellanos (@goanpeca)
#
# Licensed under the terms of the MIT License

"""

"""

# Standard library imports
import gettext


_ = gettext.gettext


# Constants
COLUMNS = (COL_START, COL_PACKAGE_TYPE, COL_NAME, COL_DESCRIPTION, COL_VERSION,
           COL_STATUS, COL_URL, COL_LICENSE, COL_INSTALL, COL_REMOVE,
           COL_UPGRADE, COL_DOWNGRADE, COL_END) = list(range(0, 13))

ACTION_COLUMNS = [COL_INSTALL, COL_REMOVE, COL_UPGRADE, COL_DOWNGRADE]
ACTIONS = (ACTION_INSTALL, ACTION_REMOVE, ACTION_UPGRADE, ACTION_DOWNGRADE,
           ACTION_CREATE, ACTION_CLONE,
           ACTION_REMOVE_ENV) = list(range(100, 107))
PACKAGE_TYPES = (CONDA_PACKAGE, PIP_PACKAGE) = ['     conda', '    pip']
PACKAGE_STATUS = (INSTALLED, NOT_INSTALLED, UPGRADABLE, DOWNGRADABLE,
                  ALL_INSTALLABLE, ALL, NOT_INSTALLABLE,
                  MIXGRADABLE) = list(range(200, 208))
COMBOBOX_VALUES_ORDERED = [_(u'Installed'), _(u'Not installed'),
                           _(u'Upgradable'), _(u'Downgradable'),
                           _(u'All installable'), _(u'All')]
COMBOBOX_VALUES = dict(zip(COMBOBOX_VALUES_ORDERED, PACKAGE_STATUS))
ROOT = 'root'
