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
import dill

logger=logging.getLogger(__name__)

def create_material(data,files):
    logger.debug(data)
    kind_of_material = data['kind_of_material']
    if kind_of_material == 'simple_solid':
        raytrace.create_simple_volume_material(data['name'], float(data['ior']))
    elif kind_of_material == 'PV_solid':
        raytrace.create_PV_material(data['name'], files['PV_file'])
    elif kind_of_material == 'simple_symmetric_surface':
        raytrace.create_reflector_lambertian_layer("rlamb", float(data['por']))
        raytrace.create_two_layers_material(data['name'], "rlamb", "rlamb")
    elif kind_of_material == 'simple_absorber_surface':
        raytrace.create_absorber_simple_material(data['name'], 1-float(data['poa']))
    material = raytrace.Material.by_name[data['name']]
    filename = '/tmp/'+data['name']+'.rtmaterial'
    with open(filename, 'wb') as f:
        dill.dump(material,f)
    return filename