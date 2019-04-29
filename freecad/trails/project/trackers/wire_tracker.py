# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Customized wire tracker from DraftTrackers.wireTracker
"""

from pivy import coin

from DraftTrackers import Tracker

from ..support.utils import Constants as C
from .base_tracker import BaseTracker

class WireTracker(BaseTracker):
    """
    Customized wire tracker
    """

    def __init__(self, doc, object_name, points, nodes=None):
        """
        Constructor
        """
        self.line = coin.SoLineSet()
        self.line.numVertices.setValue(len(points))

        super().__init__(doc, object_name, 'Wire_Tracker', nodes)

        self.draw_style = self.switch.getChild(0).getChild(0)
        self.color = self.switch.getChild(0).getChild(1)

        self.color.rgb = (0.0, 0.0, 1.0)
        self.update(points=points)
        self.on()

    def update(self, points=None, placement=None):
        """
        Update
        """

        if points:
            self.update_points(points)

        if placement:
            self.update_placement(placement)

    def update_points(self, points):
        """
        Clears and rebuilds the wire and edit trackers
        """

        self.line.numVertices.setValue(len(points))

        for _i, _pt in enumerate(points):
            self.coords.point.set1Value(_i, list(_pt))

    def update_placement(self, placement):
        """
        Updates the placement for the wire and the trackers
        """

        return

    def finalize(self):
        """
        Override of the parent method
        """
        super().finalize()