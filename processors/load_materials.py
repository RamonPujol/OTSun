import io
import logging
import sys
import os
sys.path.append("/usr/lib/freecad")
sys.path.append("/usr/lib/freecad/lib")
import FreeCAD
import raytrace
import numpy as np
import time

logger=logging.getLogger(__name__)

def processor(data, root_folder):
    files_folder = os.path.join(root_folder, 'files')
    freecad_file = os.path.join(files_folder, data['freecad_file'])
    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument
    objects = doc.Objects

    solid_material_labels = []
    faces_material_labels = []
    for obj in objects:
        # noinspection PyNoneFunctionAssignment
        label = obj.Label
        start = label.find("(")
        end = label.find(")")
        name = label[start + 1:end]
        solids = obj.Shape.Solids
        faces = obj.Shape.Faces
        if solids:  # Object is a solid
            solid_material_labels.append(name)
        else:  # Object is made of faces
            faces_material_labels.append(name)
    data['solid_material_labels'] = list(set(solid_material_labels))
    data['faces_material_labels'] = list(set(faces_material_labels))
    logger.info("Found solids %s and faces %s", data['solid_material_labels'], data['faces_material_labels'])
    FreeCAD.closeDocument(doc.Name)

    return data

