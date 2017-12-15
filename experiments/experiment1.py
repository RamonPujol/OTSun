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

#logging.getLogger().setLevel(logging.DEBUG)
logger=logging.getLogger(__name__)


def experiment(data, folder):
    phi1 = float(data['phi1']) + 0.000001 #0 + 0.0000001 # TODO: pq sumar?
    phi2 = float(data['phi2']) + 0.000001 #0
    phidelta = float(data['phidelta']) #0.1
    theta1 = float(data['theta1']) + 0.000001 #0 + 0.0000001 # TODO: pq sumar?
    theta2 = float(data['theta2']) + 0.000001 #0
    thetadelta = float(data['thetadelta']) #0.1
    number_of_rays = 10
    aperture_collector = 1. * 1. * 1.0
    lambda1 = float(data['lambda1']) # # 295.0
    lambda2 = float(data['lambda2']) # # 810.5
    lambdadelta = float(data['lambdadelta']) # # 0.5
    freecad_file = os.path.join(folder, data['freecad_file'])
    PV_file = os.path.join(folder, data['PV_file'])

    logger.debug("in exp1", locals())

    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    raytrace.create_reflector_lambertian_layer("rlamb", 1.0)
    raytrace.create_two_layers_material("RLamb", "rlamb", "rlamb")

    file_Si = PV_file #'Perovs.txt'  # change for your path
    raytrace.create_PV_material("PV1", file_Si)

    sel = doc.Objects
    current_scene = raytrace.Scene(sel)
    ##### data_file_spectrum = 'ASTMG173-direct.txt'
    # light_spectrum = raytrace.create_CDF_from_PDF(data_file_spectrum)
    # Buie_model = raytrace.BuieDistribution(0.05)
    Buie_model = None

    destfolder = folder + '.output'
    os.makedirs(destfolder)
    outfile = open(os.path.join(destfolder,'kkk4.txt'), 'w')
    outfile_PV = open(os.path.join(destfolder,'PV-10000-CAS4-kk.txt'), 'w')
    outfile_PV_values = open(os.path.join(destfolder,'PV_values_1micro.txt'), 'w')
    outfile_Source_lambdas = open(os.path.join(destfolder,'Source_lambdas_1micro.txt'), 'w')
    outfile_Source_lambdas.write("%s %s" % (aperture_collector * 0.001 * 0.001, "# Collector aperture in m2") + '\n')
    outfile_Source_lambdas.write("%s %s" % (number_of_rays, "# Rays per wavelength") + '\n')
    outfile_Source_lambdas.write("%s %s" % (lambdadelta, "# Step of wavelength in nm") + '\n')

    Source_lambdas = []
    PV_energy = []
    PV_wavelength = []
    PV_values = []
    t0 = time.time()
    for ph in np.arange(phi1, phi2, phidelta):
        for th in np.arange(theta1, theta2, thetadelta):
            for w in np.arange(lambda1, lambda2, lambdadelta):
                logger.debug("experiment1: %s, %s, %s",ph,th,w)
                light_spectrum = w
                Source_lambdas.append(w)
                main_direction = raytrace.polar_to_cartesian(ph, th) * -1.0  # Sun direction vector
                emitting_region = raytrace.SunWindow(current_scene, main_direction)
                l_s = raytrace.LightSource(current_scene, emitting_region, light_spectrum, 1.0, Buie_model)
                exp = raytrace.Experiment(current_scene, l_s, number_of_rays)

                exp.run()
                efficiency = (exp.captured_energy / aperture_collector) / (
                        exp.number_of_rays / exp.light_source.emitting_region.aperture)
                t1 = time.time()
                # print ("%s %s %s %s" % (w, th, efficiency, t1 - t0) + '\n')
                outfile.write("%s %s %s %s" % (ph, th, efficiency, t1 - t0) + '\n')
                PV_energy.append(exp.PV_energy)
                PV_wavelength.append(exp.PV_wavelength)
                PV_values.append(exp.PV_values)

    xarray = np.array(np.concatenate(PV_energy))
    yarray = np.array(np.concatenate(PV_wavelength))
    datacomp = np.array([xarray, yarray])
    datacomp = datacomp.T
    data_PV_values = np.array(np.concatenate(PV_values))
    data_Source_lambdas = np.array(Source_lambdas)
    np.savetxt(outfile_PV, datacomp, fmt=['%f', '%f'])
    np.savetxt(outfile_PV_values, data_PV_values, fmt=['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

    np.savetxt(outfile_Source_lambdas, data_Source_lambdas, fmt=['%f'])

    outfile.close()
    outfile_PV.close()
    outfile_PV_values.close()
    outfile_Source_lambdas.close()
    shutil.make_archive(folder, 'zip', destfolder)
