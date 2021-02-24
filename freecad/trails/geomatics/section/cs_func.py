
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
import Part, MeshPart
import copy, math

class CSFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    @staticmethod
    def section_converter(section_3d, origin):
        section_2d = []
        section_2d.append(FreeCAD.Vector(0, 0, 0))

        prev_vector = origin
        for i in section_3d:
            reduced_vector = copy.deepcopy(i)
            reduced_vector.z = prev_vector.z

            vector = prev_vector.sub(i)
            x_vector = prev_vector.sub(reduced_vector)
            length = vector.Length
            angle = x_vector.getAngle(vector)

            dx = length * math.cos(angle)
            dy = length * math.sin(angle)

            if x_vector.z < vector.z: dy = -dy
            vector_2d = section_2d[-1].add(FreeCAD.Vector(dx, dy, 0))
            section_2d.append(vector_2d)
            prev_vector = i

        section_2d.pop(0)
        return section_2d

    def create_3d_sections(self, gl, surface):
        wire_list = []
        for wire in gl.Shape.Wires:

            points = []
            for edge in wire.Edges:
                params = MeshPart.findSectionParameters(
                    edge, surface.Mesh, FreeCAD.Vector(0, 0, 1))
                params.insert(0, edge.FirstParameter+1)
                params.append(edge.LastParameter-1)

                values = [edge.valueAt(i) for i in params]
                points += values

            section_3d = MeshPart.projectPointsOnMesh(
                points, surface.Mesh, FreeCAD.Vector(0, 0, 1))

            line_segments = []
            for i in range(0, len(section_3d)-1):
                if section_3d[i] == section_3d[i+1]: continue
                line_segments.append(Part.LineSegment(section_3d[i], section_3d[i+1]))

            shape = Part.Shape(line_segments)
            wire = Part.Wire(shape.Edges)
            wire_list.append(wire)

        sections3d = Part.makeCompound(wire_list)
        return sections3d

    def draw_2d_sections(self, position, gl, surface, geometry, gaps):
        counter = 0
        buffer = 50000
        pos = position

        multi_views_nor = math.ceil(len(gl.Shape.Wires)**0.5)

        section_list = []
        for wire in gl.Shape.Wires:

            points = []
            origin = wire.Vertexes[0].Point
            for edge in wire.Edges:
                params = MeshPart.findSectionParameters(
                    edge, surface.Mesh, FreeCAD.Vector(0, 0, 1))
                params.insert(0, edge.FirstParameter+1)
                params.append(edge.LastParameter-1)

                values = [edge.valueAt(i) for i in params]
                points += values

            section_3d = MeshPart.projectPointsOnMesh(
                points, surface.Mesh, FreeCAD.Vector(0, 0, 1))

            section_2d = self.section_converter(section_3d, origin)

            draw_sec = []
            for i in section_2d:
                draw_sec.append(i.add(position))

            line_segments = []
            for i in range(0, len(draw_sec)-1):
                if draw_sec[i] == draw_sec[i+1]: continue
                line_segments.append(Part.LineSegment(draw_sec[i], draw_sec[i+1]))

            shape = Part.Shape(line_segments)
            sec = Part.Wire(shape.Edges)
            section_list.append(sec)

            if counter == multi_views_nor:
                shifting = position.x - pos.x + gaps[1]
                reposition = FreeCAD.Vector(geometry[1] + shifting, 0, 0)
                position = pos.add(reposition)
                counter = 0

            else:
                reposition = FreeCAD.Vector(0, -(geometry[0] + gaps[0]), 0)
                position = position.add(reposition)
                counter += 1

        section_draws = Part.makeCompound(section_list)
        return section_draws
