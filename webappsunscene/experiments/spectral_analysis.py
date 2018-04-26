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

    show_in_doc = None
    polarization_vector = None
    phi = float(data['phi']) + 1.E-9
    theta = float(data['theta']) + 1.E-9
    wavelength_ini = float(data['wavelength_ini'])
    wavelength_end = float(data['wavelength_end']) + 1E-4
    if data['wavelength_step'] == "":
        wavelength_step = 1.0
    else:
        wavelength_step = float(data['wavelength_step'])
    number_of_rays = int(data['numrays'])

    if data['aperture_pv'] == "":
        aperture_collector_PV = 0
    else:
        aperture_collector_PV = float(data['aperture_pv'])

    if data['aperture_th'] == "":
        aperture_collector_Th = 0
    else:
        aperture_collector_Th = float(data['aperture_th'])

    # ---
    # Inputs for Spectral Analysis
    # ---
    # for direction of the source two options: Buie model or main_direction
    if data['CSR'] == "":
        direction_distribution = None
    else:
        CSR = float(data['CSR'])  # default option main_direction
        Buie_model = raytrace.BuieDistribution(CSR)
        direction_distribution = Buie_model

    # for the internal quantum efficiency two options: constant value =< 1.0, or data file
    # internal_quantum_efficiency = 1.0  # default option equal to 1.0
    # internal_quantum_efficiency = 'D:Ramon_2015/RECERCA/RETOS-2015/Tareas/Proves-FreeCAD-2/materials-PV/iqe.txt'
    # for integral results three options: ASTMG173-direct (default option), ASTMG173-total, upload data_file_spectrum
    # --------- end

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

    # time
    # t0 = time.time()

    # objects for scene
    sel = doc.Objects
    current_scene = raytrace.Scene(sel)

    number_of_runs = 0
    for _ in np.arange(wavelength_ini, wavelength_end, wavelength_step):
        number_of_runs += 1

    statuslogger.total = number_of_runs
    for w in np.arange(wavelength_ini, wavelength_end, wavelength_step):
        light_spectrum = w
        main_direction = raytrace.polar_to_cartesian(phi, theta) * -1.0  # Sun direction vector
        emitting_region = raytrace.SunWindow(current_scene, main_direction)
        l_s = raytrace.LightSource(current_scene, emitting_region, light_spectrum, 1.0, direction_distribution,
                                   polarization_vector)
        exp = raytrace.Experiment(current_scene, l_s, number_of_rays, show_in_doc)
        exp.run()
        # print ("%s" % (w) + '\n')
        Th_energy.append(exp.Th_energy)
        Th_wavelength.append(exp.Th_wavelength)
        PV_energy.append(exp.PV_energy)
        PV_wavelength.append(exp.PV_wavelength)
        #   gran memoria podriem posar opcional
        # source_wavelength.append(exp.wavelengths)
        source_wavelength.append(w)
        if exp.PV_values:
            PV_values.append(exp.PV_values)
        if exp.points_absorber_Th:
            Th_points_absorber.append(exp.points_absorber_Th)
        #   end gran memoria podriem posar opcional
        captured_energy_pv += exp.captured_energy_PV
        captured_energy_th += exp.captured_energy_Th

        statuslogger.increment()

    # t1 = time.time()
    # print t1 - t0

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
        outfile_source_wavelengths.write("%s %s\n" % (wavelength_ini, "# Wavelength initial in nm"))
        outfile_source_wavelengths.write("%s %s\n" % (wavelength_end, "# Wavelength final in nm"))
        outfile_source_wavelengths.write("%s %s\n" % (wavelength_step, "# Step of wavelength in nm"))
        outfile_source_wavelengths.write("%s %s\n" % (number_of_rays, "# Rays per wavelength"))
        # np.savetxt(outfile_source_wavelengths, data_source_wavelength, fmt=['%f'])

    # --------- end

    # t2 = time.time()
    # print t2 - t1

    # ---
    # Output source spectrum for calculation and total energy emitted
    # ---
    source_spectrum = raytrace.spectrum_to_constant_step(data_file_spectrum, wavelength_step, wavelength_ini, wavelength_end)
    energy_emitted = np.trapz(source_spectrum[:, 1], x=source_spectrum[:, 0])
    # --------- end

    # ---
    # Outputs for thermal absorber materials (Th) in Spectral Analysis
    # ---
    if captured_energy_th > 1E-9:
        data_Th_points_absorber = np.array(np.concatenate(Th_points_absorber))
        table_Th = raytrace.make_histogram_from_experiment_results(Th_wavelength, Th_energy, wavelength_step,
                                                                   aperture_collector_Th,
                                                                   exp.light_source.emitting_region.aperture)

        table_Th = raytrace.twoD_array_to_constant_step(table_Th, wavelength_step, wavelength_ini, wavelength_end)
        spectrum_by_table_Th = source_spectrum[:, 1] * table_Th[:, 1]
        power_absorbed_from_source_Th = np.trapz(spectrum_by_table_Th, x=source_spectrum[:, 0])
        efficiency_from_source_Th = power_absorbed_from_source_Th / energy_emitted

        with open(os.path.join(destfolder, 'Th_spectral_efficiency.txt'), 'w') as outfile_Th_spectral:
            outfile_Th_spectral.write("%s\n" % ("#wavelength(nm) efficiency Th absorbed"))
            np.savetxt(outfile_Th_spectral, table_Th, fmt=['%f', '%f'])

        with open(os.path.join(destfolder, 'Th_points_absorber.txt'), 'w') as outfile_Th_points_absorber:
            outfile_Th_points_absorber.write("%s\n" % (
                "#energy_ray point_on_absorber[3] previous_point[3] normal_at_absorber_face[3]"))
            np.savetxt(outfile_Th_points_absorber, data_Th_points_absorber,
                       fmt=['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

        with open(os.path.join(destfolder, 'Th_integral_spectrum.txt'), 'w') as outfile_Th_integral_spectrum:
            outfile_Th_integral_spectrum.write("%s\n" % (
                "#power_absorbed_from_source_Th energy_emitted efficiency_from_source_Th"))
            outfile_Th_integral_spectrum.write("%s %s %s\n" % (
                power_absorbed_from_source_Th * aperture_collector_Th * 1E-6,
                energy_emitted * exp.light_source.emitting_region.aperture * 1E-6,
                efficiency_from_source_Th))
        # print power_absorbed_from_source_Th * aperture_collector_Th * 1E-6,
        # energy_emitted * exp.light_source.emitting_region.aperture * 1E-6, efficiency_from_source_Th

    # --------- end
    # t3 = time.time()
    # print t3 - t2
    # ---
    # Outputs for photovoltaic materials (PV) in Spectral Analysis
    # ---
    if captured_energy_pv > 1E-9:
        data_PV_values = np.array(np.concatenate(PV_values))
        table_PV = raytrace.make_histogram_from_experiment_results(PV_wavelength, PV_energy, wavelength_step,
                                                                   aperture_collector_PV,
                                                                   exp.light_source.emitting_region.aperture)

        table_PV = raytrace.twoD_array_to_constant_step(table_PV, wavelength_step, wavelength_ini, wavelength_end)
        spectrum_by_table_PV = source_spectrum[:, 1] * table_PV[:, 1]
        power_absorbed_from_source_PV = np.trapz(spectrum_by_table_PV, x=source_spectrum[:, 0])
        efficiency_from_source_PV = power_absorbed_from_source_PV / energy_emitted

        # iqe = internal_quantum_efficiency
        # SR = raytrace.spectral_response(table_PV, iqe)
        # ph_cu = raytrace.photo_current(SR, source_spectrum)

        with open(os.path.join(destfolder, 'PV_spectral_efficiency.txt'), 'w') as outfile_PV_spectral:
            outfile_PV_spectral.write("%s\n" % ("#wavelength(nm) efficiency_PV_absorbed"))
            np.savetxt(outfile_PV_spectral, table_PV, fmt=['%f', '%f'])

        with open(os.path.join(destfolder, 'PV_paths_values.txt'), 'w') as outfile_PV_paths_values:
            outfile_PV_paths_values.write("%s\n" % (
                "#first_point_in_PV[3]"
                "second_point_in_PV[3]"
                "energy_ray_first_point"
                "energy_ray_second_point"
                "wavelength_ray(nm)"
                "absortion_coefficient_alpha(mm-1)"
                "incident_angle(deg.)"))
            np.savetxt(outfile_PV_paths_values, data_PV_values,
                       fmt=['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

        # with open(os.path.join(destfolder, 'spectral_response_PV-a.txt'), 'w') as outfile_spectral_response_PV:
         #   np.savetxt(outfile_spectral_response_PV, SR, fmt=['%f', '%f'])

        #with open(os.path.join(destfolder, 'PV_integral_spectrum-a.txt'), 'w') as outfile_PV_integral_spectrum:
        #    outfile_PV_integral_spectrum.write("%s %s %s %s\n" % (
        #        "# power_absorbed_from_source_PV;   ", "energy_emitted;   ", "efficiency_from_source_PV;   ",
        #        "photocurrent (A/m2);   "))
        #    outfile_PV_integral_spectrum.write("%s %s %s\n" % (
        #        power_absorbed_from_source_PV * aperture_pv * 1E-6,
        #        energy_emitted * exp.light_source.emitting_region.aperture * 1E-6,
        #        efficiency_from_source_PV))
        # print power_absorbed_from_source_PV * aperture_collector_PV * 1E-6,
        # energy_emitted * exp.light_source.emitting_region.aperture * 1E-6, efficiency_from_source_PV, ph_cu

    # --------- end
    # t4 = time.time()
    # print t4 - t3
