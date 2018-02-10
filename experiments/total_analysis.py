import logging
import sys
import os
sys.path.append("/usr/lib/freecad")
sys.path.append("/usr/lib/freecad/lib")
import FreeCAD
import raytrace
import numpy as np
import multiprocessing
from utils.statuslogger import StatusLogger

logger=logging.getLogger(__name__)


def experiment(data, root_folder):
    global doc
    global current_scene

    CSR = 0.05
    Buie_model = raytrace.BuieDistribution(CSR)
    direction_distribution = Buie_model

    _ROOT = os.path.abspath(os.path.dirname(__file__))
    data_file_spectrum = os.path.join(_ROOT, 'data', 'ASTMG173-direct.txt')
    destfolder = os.path.join(root_folder, 'output')
    try:
        os.makedirs(destfolder)
    except:
        pass  # we suppose it already exists

    show_in_doc = None
    polarization_vector = None
    phi_ini = float(data['phi_ini']) + 0.000001
    phi_end = float(data['phi_end']) + 0.000001
    phi_step = float(data['phi_step'])
    theta_ini = float(data['theta_ini']) + 0.000001
    theta_end = float(data['theta_end']) + 0.000001
    theta_step = float(data['theta_step'])

    if data['aperture_pv'] == "":
        aperture_pv = 0
    else:
        aperture_pv = float(data['aperture_pv'])

    if data['aperture_th'] == "":
        aperture_th = 0
    else:
        aperture_th = float(data['aperture_th'])

    light_spectrum = raytrace.create_CDF_from_PDF(data_file_spectrum)

    number_of_rays = int(data['numrays'])
    files_folder = os.path.join(root_folder, 'files')
    freecad_file = os.path.join(files_folder, data['freecad_file'])
    materials_file = os.path.join(files_folder, data['materials_file'])

    raytrace.Material.load_from_zipfile(materials_file)
    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    sel = doc.Objects
    current_scene = raytrace.Scene(sel)

    manager = multiprocessing.Manager()
    statuslogger = StatusLogger(manager, 0, root_folder)

    number_of_runs = 0
    for _ in np.arange(phi_ini, phi_end, phi_step):
        for _ in np.arange(theta_ini, theta_end, theta_step):
            number_of_runs += 1

    statuslogger.total = number_of_runs

    results = []
    for ph in np.arange(phi_ini, phi_end, phi_step):
        for th in np.arange(theta_ini, theta_end, theta_step):
            main_direction = raytrace.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector
            emitting_region = raytrace.SunWindow(current_scene, main_direction)
            l_s = raytrace.LightSource(current_scene, emitting_region, light_spectrum, 1.0, direction_distribution,
                                       polarization_vector)
            exp = raytrace.Experiment(current_scene, l_s, number_of_rays, show_in_doc)
            exp.run()
            if aperture_th != 0.0:
                efficiency_from_source_th = (exp.captured_energy_Th /aperture_th) / (
                        exp.number_of_rays/exp.light_source.emitting_region.aperture)
            else:
                efficiency_from_source_th = 0.0
            if aperture_pv != 0.0:
                efficiency_from_source_pv = (exp.captured_energy_PV /aperture_pv) / (
                        exp.number_of_rays/exp.light_source.emitting_region.aperture)
            else:
                efficiency_from_source_pv = 0.0
            # print ("%.3f %.3f %.6f %.6f %s" %
            #   (ph, th, efficiency_from_source_th, efficiency_from_source_pv, t1-t0)+ '\n')
            # outfile_effciency_results.write("%.3f %.3f %.6f %.6f" %
            #   (ph, th, efficiency_from_source_th, efficiency_from_source_pv)+ '\n')
            results.append((ph, th, efficiency_from_source_th, efficiency_from_source_pv))
            statuslogger.increment()

    power_emitted_by_m2 = raytrace.integral_from_data_file(data_file_spectrum)

    with open(os.path.join(destfolder, 'efficiency_results-a.txt'), 'w') as outfile_efficiency_results:
        outfile_efficiency_results.write(
            "%s %s" % (aperture_th * 0.001 * 0.001, "# Collector Th aperture in m2") + '\n')
        outfile_efficiency_results.write(
            "%s %s" % (aperture_pv * 0.001 * 0.001, "# Collector PV aperture in m2") + '\n')
        outfile_efficiency_results.write("%s %s" % (power_emitted_by_m2, "# Source power emitted by m2") + '\n')
        outfile_efficiency_results.write("%s %s %s %s" % (
            "# phi;   ", "theta;   ", "efficiency_from_source_Th;   ", "efficiency_from_source_PV") + '\n')
        for result in results:
            outfile_efficiency_results.write("%.3f %.3f %.6f %.6f\n" % result)
