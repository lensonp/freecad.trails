
# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

'''
Define Surface Object functions.
'''

import FreeCAD
import Part
import copy

class GLFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    def line_orthogonal(self, line, distance, side=''):
        """
        Return the orthogonal vector pointing toward the indicated side at the
        provided position.  Defaults to left-hand side
        """

        _dir = 1.0

        _side = side.lower()

        if _side in ['r', 'rt', 'right']:
            _dir = -1.0

        start = line.Start
        end = line.End

        if (start is None) or (end is None):
            return None, None

        _delta = end.sub(start).normalize()
        _left = FreeCAD.Vector(-_delta.y, _delta.x, 0.0)

        _coord = start.add(_delta.multiply(distance*1000))

        return _coord, _left.multiply(_dir)

    def generate(self, alignment, increments, ofsets, region, horiz_pnts = True):
        """
        Generates guidelines along a selected alignment
        """
        # Get left and right offsets from centerline
        left_offset = ofsets[0]
        right_offset = ofsets[1]

        # Region limits
        start_station = region[0]
        end_station = region[1]

        # Guideline intervals
        tangent_increment = increments[0]
        curve_increment = increments[1]
        spiral_increment = increments[2]

        # Retrieve alignment data get geometry and placement
        stations = []
        if hasattr(alignment.Proxy, 'model'):
            start = alignment.Proxy.model.data['meta']['StartStation']
            length = alignment.Proxy.model.data['meta']['Length']
            end = start + length/1000

            placement = alignment.Placement.Base
            geometry = alignment.Proxy.model.data['geometry']

            for element in geometry:
                # Get starting and ending stations based on alignment
                elem_start = element.get('StartStation')
                elem_end = element.get('StartStation')+element.get('Length')/1000

                if elem_start != 0 and horiz_pnts:
                        stations.append(elem_start)

                # Generate line intervals
                if element.get('Type') == 'Line':

                    # Iterate the station range
                    for sta in range(int(elem_start), int(elem_end)):

                        # Add stations which land on increments exactly
                        if sta % tangent_increment == 0:
                            stations.append(sta)

                # Generate curve intervals
                elif element.get('Type') == 'Curve':
                    for sta in range(int(elem_start), int(elem_end)):
                        if sta % int(curve_increment) == 0:
                            stations.append(sta)

                #Generate spiral intervals
                elif element.get("Type") == 'Spiral':
                    for sta in range(int(elem_start), int(elem_end)):
                        if sta % int(spiral_increment) == 0:
                            stations.append(sta)
    
            # Add the end station
            stations.append(round(end,3))

        # Create guide lines from standart line object
        else:
            length = alignment.Length.Value
            for sta in range(0, int(length/1000)):
                if sta % int(tangent_increment/1000) == 0:
                    stations.append(sta)

            # Add the end station
            stations.append(round(length/1000,3))

        # Iterate the stations, appending what falls in the specified limits
        region_stations = []
        for sta in stations:

            if start_station <= sta <= end_station:
                region_stations.append(sta)

        region_stations.sort()

        # Iterate the final list of stations,
        # Computing coordinates and orthoginals for guidelines
        for sta in region_stations:
            if hasattr(alignment.Proxy, 'model'):
                coord, vec = alignment.Proxy.model.get_orthogonal( sta, "Left")
            else:
                coord, vec = self.line_orthogonal(alignment, sta, "Left")

            left_vec = copy.deepcopy(vec)
            right_vec = copy.deepcopy(vec)

            left_side = coord.add(left_vec.multiply(left_offset))
            right_side = coord.add(right_vec.negative().multiply(right_offset))

            left_line = Part.LineSegment(left_side, coord)
            right_line = Part.LineSegment(right_side, coord)

            # Generate guide line object and add to cluster
            shape = Part.Shape([left_line, right_line])
            wire = Part.Wire(shape.Edges)
            Part.show(wire)