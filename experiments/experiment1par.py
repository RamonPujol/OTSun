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
import shutil
import multiprocessing
import json

logger = logging.getLogger(__name__)

finished_computations_counter = None


def init_counter(args):
    """ store the counter for later use """
    global finished_computations_counter
    finished_computations_counter = args

def update_percentage(partial, total):
    percentage = (100 * partial) / total
    logger.debug('experiment is at %s percent', percentage)
    data_status = {'percentage': percentage}
    if partial == total:
        data_status['finished'] = True
    with open(status_file, 'w') as fp:
        json.dump(data_status, fp)


def computeX(args):
    ph, th, w, number_of_rays, aperture_collector = args
    logger.debug("experiment1X: %s, %s, %s", ph, th, w)
    global finished_computations_counter
    with finished_computations_counter.get_lock():
        finished_computations_counter.value += 1
    logger.debug('finished %s of %s computations', finished_computations_counter.value, total_computations)
    return (ph, th, w, 0, 0, 0, 0)


def compute(args):
    # get parameters
    ph, th, w, number_of_rays, aperture_collector = args
    logger.debug("running experiment1 with: ph=%s, th=%s, w=%s", ph, th, w)

    # prepare experiment
    main_direction = raytrace.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector
    emitting_region = raytrace.SunWindow(current_scene, main_direction)
    l_s = raytrace.LightSource(current_scene, emitting_region, w, 1.0, None)
    exp = raytrace.Experiment(current_scene, l_s, number_of_rays)

    # run experiment and compute output
    exp.run()
    efficiency = (exp.captured_energy / aperture_collector) / (
            exp.number_of_rays / exp.light_source.emitting_region.aperture)

    # update the number of finished computations
    global finished_computations_counter
    with finished_computations_counter.get_lock():
        finished_computations_counter.value += 1
        value = finished_computations_counter.value
        if (value == total_computations) or ((value % (total_computations / 100)) == 0):
            update_percentage(value, total_computations)
        logger.debug('finished %s of %s computations', value, total_computations)

    # return the results
    return (ph, th, w, efficiency, exp.PV_energy, exp.PV_wavelength, exp.PV_values)


def experiment(data, root_folder):
    global current_scene

    # get parameters of the experiment from the data dict
    phi1 = float(data['phi1']) + 0.000001  # 0 + 0.0000001 # TODO: pq sumar?
    phi2 = float(data['phi2']) + 0.000001  # 0
    phidelta = float(data['phidelta'])  # 0.1
    theta1 = float(data['theta1']) + 0.000001  # 0 + 0.0000001 # TODO: pq sumar?
    theta2 = float(data['theta2']) + 0.000001  # 0
    thetadelta = float(data['thetadelta'])  # 0.1
    number_of_rays = 10
    aperture_collector = 1. * 1. * 1.0
    lambda1 = float(data['lambda1'])  # # 295.0
    lambda2 = float(data['lambda2'])  # # 810.5
    lambdadelta = float(data['lambdadelta'])  # # 0.5
    files_folder = os.path.join(root_folder, 'files')
    freecad_file = os.path.join(files_folder, data['freecad_file'])
    PV_file = os.path.join(files_folder, data['PV_file'])

    logger.debug("in exp1", locals())

    # open FreeCAD document
    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    # create materials
    raytrace.create_reflector_lambertian_layer("rlamb", 1.0)
    raytrace.create_two_layers_material("RLamb", "rlamb", "rlamb")
    file_Si = PV_file
    raytrace.create_PV_material("PV1", file_Si)

    # prepare Scene
    sel = doc.Objects
    current_scene = raytrace.Scene(sel)
    # data_file_spectrum = 'ASTMG173-direct.txt'
    # light_spectrum = raytrace.create_CDF_from_PDF(data_file_spectrum)
    # Buie_model = raytrace.BuieDistribution(0.05)

    # Prepare input for multiprocessing
    list_pars = []
    for ph in np.arange(phi1, phi2, phidelta):
        for th in np.arange(theta1, theta2, thetadelta):
            for w in np.arange(lambda1, lambda2, lambdadelta):
                list_pars.append((ph, th, w, number_of_rays, aperture_collector))

    # Prepare shared counter of finished computations and status file
    finished_computations_counter = multiprocessing.Value('i', 0)
    global total_computations
    total_computations = len(list_pars)
    global status_file
    status_file = os.path.join(root_folder, 'status.json')

    # Prepare pool of workers and feed it
    logger.info("number of cpus: %s", multiprocessing.cpu_count())
    pool = multiprocessing.Pool(initializer=init_counter, initargs=(finished_computations_counter,))
    results = pool.map(compute, list_pars)
    logger.debug('finisehd pool.map %s, %s', len(results), len(list_pars))

    # Close document
    FreeCAD.closeDocument(doc.Name)

    # Process results
    Source_lambdas = []
    PV_energy = []
    PV_wavelength = []
    PV_values = []
    efficiencies = []

    for result in results:
        (ph, th, w, efficiency, pv_energy, pv_wavelength, pv_values) = result
        PV_energy.append(pv_energy)
        PV_wavelength.append(pv_wavelength)
        PV_values.append(pv_values)
        Source_lambdas.append(w)

    xarray = np.array(np.concatenate(PV_energy))
    yarray = np.array(np.concatenate(PV_wavelength))
    datacomp = np.array([xarray, yarray])
    datacomp = datacomp.T
    data_PV_values = np.array(np.concatenate(PV_values))
    data_source_lambdas = np.array(Source_lambdas)

    # Write files with output
    destfolder = os.path.join(root_folder, 'output')
    os.makedirs(destfolder)
    with open(os.path.join(destfolder, 'kkk4.txt'), 'w') as outfile:
        for result in results:
            outfile.write(str(result) + '\n')
    with open(os.path.join(destfolder, 'PV-10000-CAS4-kk.txt'), 'w') as outfile_PV:
        np.savetxt(outfile_PV, datacomp, fmt=['%f', '%f'])
    with open(os.path.join(destfolder, 'PV_values_1micro.txt'), 'w') as outfile_PV_values:
        np.savetxt(outfile_PV_values, data_PV_values,
                   fmt=['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])
    with open(os.path.join(destfolder, 'Source_lambdas_1micro.txt'), 'w') as outfile_Source_lambdas:
        outfile_Source_lambdas.write("%s %s" % (aperture_collector * 0.001 * 0.001,
                                                "# Collector aperture in m2") + '\n')
        outfile_Source_lambdas.write("%s %s" % (number_of_rays, "# Rays per wavelength") + '\n')
        outfile_Source_lambdas.write("%s %s" % (lambdadelta, "# Step of wavelength in nm") + '\n')
        np.savetxt(outfile_Source_lambdas, data_source_lambdas, fmt=['%f'])

    # Prepare zipfile
#    shutil.make_archive(destfolder, 'zip', destfolder)
