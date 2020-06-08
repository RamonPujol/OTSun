import logging
import sys
import os
sys.path.append("/usr/lib/freecad")
sys.path.append("/usr/lib/freecad/lib")
import FreeCAD
import otsun
import numpy as np
import time
from multiprocessing import Queue, Process, Manager, active_children
from webappsunscene.utils.statuslogger import StatusLogger

logger = logging.getLogger(__name__)
data_consumer_queue = Queue()
n_cpu = 20

def data_consumer():
    data = []
    while True:
        m = data_consumer_queue.get()
        if m == 'kill':
            logger.info("Finished getting results")
            break
        logger.info(f"appending {m}")
        data.append(m)
    data.sort()

    power_emitted_by_m2 = otsun.integral_from_data_file(data_file_spectrum)

    logger.info("Writing files")
    with open(os.path.join(destfolder, 'efficiency_results.txt'), 'w') as outfile_efficiency_results:
        outfile_efficiency_results.write(
            "%s %s" % (aperture_collector_Th * 0.001 * 0.001, "# Collector Th aperture in m2") + '\n')
        outfile_efficiency_results.write(
            "%s %s" % (aperture_collector_PV * 0.001 * 0.001, "# Collector PV aperture in m2") + '\n')
        outfile_efficiency_results.write("%s %s" % (power_emitted_by_m2, "# Source power emitted by m2") + '\n')
        outfile_efficiency_results.write("%s %s" % (number_of_rays, "# Rays emitted")+ '\n')
        outfile_efficiency_results.write("%s" % (
            "#phi theta efficiency_from_source_Th efficiency_from_source_PV") + '\n')
        for result in data:
            outfile_efficiency_results.write("%.3f %.3f %.6f %.6f\n" % result)


def compute(*args):
    ph, th, statuslogger = args

    main_direction = otsun.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector

    if move_elements:
        tracking = otsun.MultiTracking(main_direction, current_scene)
        tracking.make_movements()

    emitting_region = otsun.SunWindow(current_scene, main_direction)
    l_s = otsun.LightSource(current_scene, emitting_region, light_spectrum, 1.0, direction_distribution,
                            polarization_vector)

    exp = otsun.Experiment(current_scene, l_s, number_of_rays, show_in_doc)
    logger.info("launching experiment %s", [os.getpid(), ph, th, main_direction])
    try:
        exp.run()
    except:
        logger.error("computation ended with an error")
        return
    if aperture_collector_Th != 0.0:
        efficiency_from_source_th = (exp.captured_energy_Th / aperture_collector_Th) / (
                exp.number_of_rays / exp.light_source.emitting_region.aperture)
    else:
        efficiency_from_source_th = 0.0
    if aperture_collector_PV != 0.0:
        efficiency_from_source_pv = (exp.captured_energy_PV / aperture_collector_PV) / (
                exp.number_of_rays / exp.light_source.emitting_region.aperture)
    else:
        efficiency_from_source_pv = 0.0
    data_consumer_queue.put((ph, th, efficiency_from_source_th, efficiency_from_source_pv))

    if move_elements:
        tracking.undo_movements()

    statuslogger.increment()


def computation(data, root_folder):
    # global doc
    global current_scene

    manager = Manager()
    statuslogger = StatusLogger(manager, 0, root_folder)

    logger.info("experiment from total_analysis got called")
    _ROOT = os.path.abspath(os.path.dirname(__file__))
    global data_file_spectrum
    data_file_spectrum = os.path.join(_ROOT, 'data', 'ASTMG173-direct.txt')
    global destfolder
    destfolder = os.path.join(root_folder, 'output')
    try:
        os.makedirs(destfolder)
    except:
        pass  # we suppose it already exists

    global polarization_vector
    polarization_vector = None
    phi_ini = float(data['phi_ini']) + 1.E-9
    phi_end = float(data['phi_end']) + 1.E-4
    if data['phi_step'] == "" or float(data['phi_step'])==0:
        phi_step = 1.0
    else:
        phi_step = float(data['phi_step'])

    theta_ini = float(data['theta_ini']) + 1.E-9
    theta_end = float(data['theta_end']) + 1.E-4
    if data['theta_step'] == "" or float(data['theta_step']==0):
        theta_step = 1.0
    else:
        theta_step = float(data['theta_step'])

    global number_of_rays
    number_of_rays = int(data['numrays'])

    global aperture_collector_PV
    if data['aperture_pv'] == "":
        aperture_collector_PV = 0
    else:
        aperture_collector_PV = float(data['aperture_pv'])

    global aperture_collector_Th
    if data['aperture_th'] == "":
        aperture_collector_Th = 0
    else:
        aperture_collector_Th = float(data['aperture_th'])

    # ---
    # Inputs for Total Analysis
    # ---
    # for direction of the source two options: Buie model or main_direction
    global direction_distribution
    if data['CSR'] == "":
        direction_distribution = None # default option main_direction
    else:
        CSR = float(data['CSR'])
        Buie_model = otsun.buie_distribution(CSR)
        direction_distribution = Buie_model

    global light_spectrum
    light_spectrum = otsun.cdf_from_pdf_file(data_file_spectrum)

    files_folder = os.path.join(root_folder, 'files')
    freecad_file = os.path.join(files_folder, data['freecad_file'])
    materials_file = os.path.join(files_folder, data['materials_file'])

    otsun.Material.by_name = {}
    otsun.Material.load_from_json_zip(materials_file)
    doc = FreeCAD.openDocument(freecad_file)

    sel = doc.Objects
    current_scene = otsun.Scene(sel)


    list_pars = []
    for ph in np.arange(phi_ini, phi_end, phi_step):
        for th in np.arange(theta_ini, theta_end, theta_step):
            list_pars.append((ph, th, statuslogger))

    global move_elements
    move_elements = data.get('move_scene', 'no') == 'yes'

    statuslogger.total = len(list_pars)
    global show_in_doc
    show_in_doc = None

    data_consumer_process = Process(target=data_consumer)
    data_consumer_process.start()
    remaining = list_pars[:]
    processes = []
    while remaining:
        free_slots = n_cpu - len(active_children())
        # print(f"{free_slots} free slots")
        process_now = remaining[:free_slots]
        remaining = remaining[free_slots:]
        for args in process_now:
            p = Process(target=compute, args=args)
            p.start()
            processes.append(p)
        time.sleep(0.1)
    logger.info("All tasks queued")
    for p in processes:
        p.join()
    # for ch in active_children():
    #     if ch != data_consumer_process:
    #         logger.info(f"Joining {ch.pid}")
    #         ch.join()
    logger.info("Putting poison")
    data_consumer_queue.put('kill')
    data_consumer_process.join()

