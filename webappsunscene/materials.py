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
    if kind_of_material == 'constant_ior':
        raytrace.create_simple_volume_material(data['name'],
                                                    float(data['ior']),
                                                    None if data['ex_co'] == None else float(data['ex_co']))
    elif kind_of_material == 'variable_ior':
        raytrace.create_wavelength_volume_material(data['name'], files['ior_file'])
    elif kind_of_material == 'PV_volume':
        raytrace.create_PV_material(data['name'], files['PV_file'])
    elif kind_of_material == 'opaque_simple_layer':
        raytrace.create_opaque_simple_layer(data['name'])
    elif kind_of_material == 'transparent_simple_layer':
        raytrace.create_transparent_simple_layer(data['name'], float(data['pot']))
    elif kind_of_material == 'absorber_simple_layer':
        raytrace.create_absorber_simple_layer(data['name'], float(data['poa']))
    elif kind_of_material == 'absorber_lambertian_layer':
        raytrace.create_absorber_lambertian_layer(data['name'], float(data['poa']))
    elif kind_of_material == 'absorber_TW_model_layer':
        raytrace.create_absorber_TW_model_layer(data['name'],
                                                float(data['poa']),
                                                float(data['b_constant']),
                                                float(data['c_constant']))
    elif kind_of_material == 'reflector_specular_layer':
        raytrace.create_reflector_specular_layer(data['name'],
                                                    float(data['por']),
                                                    None if data['sigma_1'] == '' else float(data['sigma_1']),
                                                    None if data['sigma_2'] == '' else float(data['sigma_2']),
                                                    None if data['k'] == '' else float(data['k']))
    elif kind_of_material == 'reflector_lambertian_layer':
        raytrace.create_reflector_lambertian_layer(data['name'], float(data['por']))
    elif kind_of_material == 'metallic_specular_layer':
        raytrace.create_metallic_specular_layer(data['name'],
                                                    files['ior_file'],
                                                    None if data['sigma_1'] == '' else float(data['sigma_1']),
                                                    None if data['sigma_2'] == '' else float(data['sigma_2']),
                                                    None if data['k'] == '' else float(data['k']))
    elif kind_of_material == 'polarized_coating_reflector_layer':
        raytrace.create_polarized_coating_reflector_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'polarized_coating_transparent_layer':
        raytrace.create_polarized_coating_transparent_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'polarized_coating_absorber_layer':
        raytrace.create_polarized_coating_absorber_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'two_layers_material':
        mat_front = raytrace.Material.load_from_file(file_front)
        mat_back = raytrace.Material.load_from_file(file_back)
        name_front = mat_front.name
        name_back = mat_back.name
        raytrace.create_polarized_coating_absorber_layer(data['name'], name_front, name_back)
    elif kind_of_material == 'simple_symmetric_surface':
        raytrace.create_reflector_lambertian_layer("rlamb", float(data['por']))
        raytrace.create_two_layers_material(data['name'], "rlamb", "rlamb")
    elif kind_of_material == 'simple_absorber_surface':
        raytrace.create_absorber_simple_material(data['name'], 1-float(data['poa']))
    material = raytrace.Material.by_name[data['name']]
    filename = '/tmp/'+data['name']+'.rtmaterial'
    with open(filename, 'wb') as f:
        dill.dump(material, f)
    return filename
