import logging
import sys
import os
from uuid import uuid4

sys.path.append("/usr/lib/freecad")
sys.path.append("/usr/lib/freecad/lib")
import otsun
# import dill

# import dummy.default_settings
UPLOAD_FOLDER = "/tmp/" # dummy.default_settings.UPLOAD_FOLDER
# TODO: customize
#config = os.environ.get('OTSUN_CONFIG_FILE')
#if config:
#    execfile(config)

logger = logging.getLogger(__name__)

if not os.path.exists(UPLOAD_FOLDER):
    logger.info('creating upload folder')
    os.makedirs(UPLOAD_FOLDER)
else:
    if not os.access(UPLOAD_FOLDER, os.W_OK):
        UPLOAD_FOLDER += str(uuid4())
        os.makedirs(UPLOAD_FOLDER)

def create_material(data, files):
    logger.debug(data)
    kind_of_material = data['kind_of_material']
    if kind_of_material == 'constant_ior':
        otsun.create_simple_volume_material(data['name'],
                                            float(data['ior']),
                                            None if data['at_co'] == '' else float(data['at_co']))
    elif kind_of_material == 'variable_ior':
        otsun.create_wavelength_volume_material(data['name'], files['ior_file'])
    elif kind_of_material == 'PV_volume':
        otsun.create_PV_material(data['name'], files['PV_file'])
    elif kind_of_material == 'polarized_thin_film':
        if data['front_vacuum']:
            if data['back_vacuum']:
                otsun.create_polarized_thin_film(data['name'], files['thin_film_file'],
                                                 "Vacuum", "Vacuum")
            else:
                otsun.create_polarized_thin_film(data['name'], files['thin_film_file'],
                                                 "Vacuum", files['back_file'])
        else:
            if data['back_vacuum']:
                otsun.create_polarized_thin_film(data['name'], files['thin_film_file'],
                                                 files['front_file'], "Vacuum")
            else:
                otsun.create_polarized_thin_film(data['name'], files['thin_film_file'],
                                                 files['front_file'], files['back_file'])

    elif kind_of_material == 'opaque_simple_layer':
        otsun.create_opaque_simple_layer(data['name'])
    elif kind_of_material == 'transparent_simple_layer':
        otsun.create_transparent_simple_layer(data['name'], float(data['pot']))
    elif kind_of_material == 'absorber_simple_layer':
        otsun.create_absorber_simple_layer(data['name'], float(data['poa']))
    elif kind_of_material == 'absorber_lambertian_layer':
        otsun.create_absorber_lambertian_layer(data['name'], float(data['poa']))
    elif kind_of_material == 'absorber_TW_model_layer':
        otsun.create_absorber_TW_model_layer(data['name'],
                                             float(data['poa']),
                                             float(data['b_constant']),
                                             float(data['c_constant']))
    elif kind_of_material == 'reflector_specular_layer':
        otsun.create_reflector_specular_layer(data['name'],
                                              float(data['por']),
                                              None if data['sigma_1'] == '' else float(data['sigma_1']),
                                              None if data['sigma_2'] == '' else float(data['sigma_2']),
                                              None if data['k'] == '' else float(data['k']))
    elif kind_of_material == 'reflector_lambertian_layer':
        otsun.create_reflector_lambertian_layer(data['name'], float(data['por']))
    elif kind_of_material == 'metallic_specular_layer':
        otsun.create_metallic_specular_layer(data['name'],
                                             files['ior_file'],
                                             None if data['sigma_1'] == '' else float(data['sigma_1']),
                                             None if data['sigma_2'] == '' else float(data['sigma_2']),
                                             None if data['k'] == '' else float(data['k']))
    elif kind_of_material == 'metallic_lambertian_layer':
        otsun.create_metallic_lambertian_layer(data['name'], files['ior_file'])
    elif kind_of_material == 'polarized_coating_reflector_layer':
        otsun.create_polarized_coating_reflector_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'polarized_coating_transparent_layer':
        otsun.create_polarized_coating_transparent_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'polarized_coating_absorber_layer':
        otsun.create_polarized_coating_absorber_layer(data['name'], files['coating_file'])
    elif kind_of_material == 'two_layers_material':
        # name_front = otsun.Material.load_from_file(files['file_front'])
        # name_back = otsun.Material.load_from_file(files['file_back'])
        ## mat_front = dill.load(files['file_front'])
        ## mat_back = dill.load(files['file_back'])
        mat_front_name = otsun.Material.load_from_json_fileobject(files['file_front'])
        mat_back_name = otsun.Material.load_from_json_fileobject(files['file_back'])
        #otsun.Material.by_name[mat_back.name] = mat_back
        #otsun.Material.by_name[mat_front.name] = mat_front
        otsun.create_two_layers_material(data['name'], mat_front_name, mat_back_name)
    elif kind_of_material == 'simple_symmetric_surface':
        otsun.create_reflector_lambertian_layer("rlamb", float(data['por']))
        otsun.create_two_layers_material(data['name'], "rlamb", "rlamb")
    elif kind_of_material == 'simple_absorber_surface':
        otsun.create_absorber_simple_layer(data['name'], 1 - float(data['poa']))
    material = otsun.Material.by_name[data['name']]
    temp_folder = os.path.join(UPLOAD_FOLDER, str(uuid4()))
    os.makedirs(temp_folder)
    # filename = os.path.join(temp_folder, data['name'] + '.rtmaterial')
    # filename = '/tmp/'+data['name']+'.rtmaterial'
    # with open(filename, 'wb') as f:
    #     dill.dump(material, f)
    filename = os.path.join(temp_folder, data['name'] + '.otmaterial')
    material.save_to_json_file(filename)
    return filename
