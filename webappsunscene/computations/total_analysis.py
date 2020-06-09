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

def data_consumer(common_data):
    data = []
    while True:
        m = data_consumer_queue.get()
        if m == 'kill':
            logger.info("Finished getting results")
            break
        logger.info(f"appending {m}")
        data.append(m)
    data.sort()

    power_emitted_by_m2 = otsun.integral_from_data_file(common_data['data_file_spectrum'])

    logger.info("Writing files")
    with open(os.path.join(common_data['destfolder'], 'efficiency_results.txt'), 'w') as outfile_efficiency_results:
        outfile_efficiency_results.write(
            "%s %s" % (common_data['aperture_collector_Th'] * 0.001 * 0.001, "# Collector Th aperture in m2") + '\n')
        outfile_efficiency_results.write(
            "%s %s" % (common_data['aperture_collector_PV'] * 0.001 * 0.001, "# Collector PV aperture in m2") + '\n')
        outfile_efficiency_results.write("%s %s" % (power_emitted_by_m2, "# Source power emitted by m2") + '\n')
        outfile_efficiency_results.write("%s %s" % (common_data['number_of_rays'], "# Rays emitted")+ '\n')
        outfile_efficiency_results.write("%s" % (
            "#phi theta efficiency_from_source_Th efficiency_from_source_PV") + '\n')
        for result in data:
            outfile_efficiency_results.write("%.3f %.3f %.6f %.6f\n" % result)


def compute(*args):
    ph, th, common_data = args

    main_direction = otsun.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector

    if common_data['move_elements']:
        tracking = otsun.MultiTracking(main_direction, common_data['current_scene'])
        tracking.make_movements()

    emitting_region = otsun.SunWindow(common_data['current_scene'], main_direction)
    l_s = otsun.LightSource(common_data['current_scene'], emitting_region, common_data['light_spectrum'], 1.0,
                            common_data['direction_distribution'],
                            common_data['polarization_vector'])

    exp = otsun.Experiment(common_data['current_scene'], l_s,
                           common_data['number_of_rays'], common_data['show_in_doc'])
    logger.info("launching experiment %s", [os.getpid(), ph, th, main_direction])
    try:
        exp.run()
    except:
        logger.error("computation ended with an error")
        return
    if common_data['aperture_collector_Th'] != 0.0:
        efficiency_from_source_th = (exp.captured_energy_Th / common_data['aperture_collector_Th']) / (
                exp.number_of_rays / exp.light_source.emitting_region.aperture)
    else:
        efficiency_from_source_th = 0.0
    if common_data['aperture_collector_PV'] != 0.0:
        efficiency_from_source_pv = (exp.captured_energy_PV / common_data['aperture_collector_PV']) / (
                exp.number_of_rays / exp.light_source.emitting_region.aperture)
    else:
        efficiency_from_source_pv = 0.0
    data_consumer_queue.put((ph, th, efficiency_from_source_th, efficiency_from_source_pv))

    if common_data['move_elements']:
        tracking.undo_movements()

    common_data['statuslogger'].increment()


def computation(data, root_folder):

    logger.info("experiment from total_analysis got called")

    #
    # Prepare common data
    #

    common_data = {}

    manager = Manager()
    common_data['statuslogger'] = StatusLogger(manager, 0, root_folder)

    _ROOT = os.path.abspath(os.path.dirname(__file__))

    common_data['data_file_spectrum'] = os.path.join(_ROOT, 'data', 'ASTMG173-direct.txt')
    common_data['light_spectrum'] = otsun.cdf_from_pdf_file(common_data['data_file_spectrum'])

    common_data['destfolder'] = os.path.join(root_folder, 'output')
    try:
        os.makedirs(common_data['destfolder'])
    except:
        pass  # we suppose it already exists

    if data['CSR'] == "":
        common_data['direction_distribution'] = None # default option main_direction
    else:
        CSR = float(data['CSR'])
        Buie_model = otsun.buie_distribution(CSR)
        common_data['direction_distribution'] = Buie_model


    common_data['show_in_doc'] = None

    common_data['number_of_rays'] = int(data['numrays'])

    if data['aperture_pv'] == "":
        common_data['aperture_collector_PV'] = 0
    else:
        common_data['aperture_collector_PV'] = float(data['aperture_pv'])

    if data['aperture_th'] == "":
        common_data['aperture_collector_Th'] = 0
    else:
        common_data['aperture_collector_Th'] = float(data['aperture_th'])

    common_data['move_elements'] = data.get('move_scene', 'no') == 'yes'

    common_data['polarization_vector'] = None

    #
    # Load parameters from user input
    #

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

    #
    # Load document and materials
    #

    files_folder = os.path.join(root_folder, 'files')
    freecad_file = os.path.join(files_folder, data['freecad_file'])
    materials_file = os.path.join(files_folder, data['materials_file'])

    otsun.Material.by_name = {}
    otsun.Material.load_from_json_zip(materials_file)

    doc = FreeCAD.openDocument(freecad_file)
    sel = doc.Objects

    common_data['current_scene'] = otsun.Scene(sel)

    #
    # Prepare computations
    #

    list_pars = []
    for ph in np.arange(phi_ini, phi_end, phi_step):
        for th in np.arange(theta_ini, theta_end, theta_step):
            list_pars.append((ph, th, common_data))

    common_data['statuslogger'].total = len(list_pars)

    #
    # Prepare consumer
    #

    data_consumer_process = Process(target=data_consumer, args=(common_data,))
    data_consumer_process.start()

    #
    # Launch computations
    #

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

    #
    # Finish computations and consumer
    #

    for p in processes:
        p.join()
    logger.info("Putting poison")
    data_consumer_queue.put('kill')
    data_consumer_process.join()

