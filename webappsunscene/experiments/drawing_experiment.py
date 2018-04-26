import logging
import sys
import os
sys.path.append("/usr/lib/freecad")
sys.path.append("/usr/lib/freecad/lib")
import FreeCAD
import raytrace
import numpy as np
import multiprocessing
from webappsunscene.utils.statuslogger import StatusLogger

logger = logging.getLogger(__name__)


def experiment(data, root_folder):
    global doc
    global current_scene

    _ROOT = os.path.abspath(os.path.dirname(__file__))
    data_file_spectrum = os.path.join(_ROOT, 'data', 'ASTMG173-direct.txt')
    destfolder = os.path.join(root_folder, 'output')
    try:
        os.makedirs(destfolder)
    except:
        pass  # we suppose it already exists

    polarization_vector = None
    phi = float(data['phi']) + 1.E-9
    theta = float(data['theta']) + 1.E-9
    wavelength = float(data['wavelength'])
    number_of_rays = int(data['numrays'])

    if data['aperture_pv'] == "":
        aperture_collector_PV = 0
    else:
        aperture_collector_PV = float(data['aperture_pv'])

    if data['aperture_th'] == "":
        aperture_collector_Th = 0
    else:
        aperture_collector_Th = float(data['aperture_th'])

    # for direction of the source two options: Buie model or main_direction
    if data['CSR'] == "":
        direction_distribution = None
    else:
        CSR = float(data['CSR'])  # default option main_direction
        Buie_model = raytrace.BuieDistribution(CSR)
        direction_distribution = Buie_model

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

    # ---
    # Magnitudes used for outputs in Spectral Analysis
    # ---
    captured_energy_pv = 0.0
    captured_energy_th = 0.0
    source_wavelength = []
    Th_energy = []
    Th_wavelength = []
    Th_points_absorber = []
    PV_energy = []
    PV_wavelength = []
    PV_values = []
    # --------- end

    number_of_runs = 1

    statuslogger.total = number_of_runs
    show_in_doc = doc
    w = wavelength
    light_spectrum = w
    main_direction = raytrace.polar_to_cartesian(phi, theta) * -1.0  # Sun direction vector
    emitting_region = raytrace.SunWindow(current_scene, main_direction)
    l_s = raytrace.LightSource(current_scene, emitting_region, light_spectrum, 1.0, direction_distribution,
                               polarization_vector)
    exp = raytrace.Experiment(current_scene, l_s, number_of_rays, show_in_doc)
    exp.run(show_in_doc)
    Th_energy.append(exp.Th_energy)
    Th_wavelength.append(exp.Th_wavelength)
    PV_energy.append(exp.PV_energy)
    PV_wavelength.append(exp.PV_wavelength)
    source_wavelength.append(w)
    if exp.PV_values:
        PV_values.append(exp.PV_values)
    if exp.points_absorber_Th:
        Th_points_absorber.append(exp.points_absorber_Th)
    captured_energy_pv += exp.captured_energy_PV
    captured_energy_th += exp.captured_energy_Th

    statuslogger.increment()

    all_obj = doc.Objects
    for obj in all_obj:
        logger.debug('Object %s', obj.Name)

    doc.recompute()
    doc.saveAs(os.path.join(destfolder,'drawing.FCStd'))

    # Close document
    FreeCAD.closeDocument(doc.Name)
    # ---
    # Output file for wavelengths emitted by the source
    # ---
    data_source_wavelength = np.array(source_wavelength)
    data_source_wavelength = data_source_wavelength.T
    source_wavelengths_file = os.path.join(destfolder, 'source_wavelengths.txt')
    with open(source_wavelengths_file, 'w') as outfile_source_wavelengths:
        outfile_source_wavelengths.write(
            "%s %s\n" % (aperture_collector_Th * 0.001 * 0.001, "# Collector Th aperture in m2"))
        outfile_source_wavelengths.write(
            "%s %s\n" % (aperture_collector_PV * 0.001 * 0.001, "# Collector PV aperture in m2"))
        outfile_source_wavelengths.write("%s %s\n" % (wavelength, "# Wavelength in nm"))
        outfile_source_wavelengths.write("%s %s\n" % (number_of_rays, "# Rays to plot"))
    # --------- end
    # ---

