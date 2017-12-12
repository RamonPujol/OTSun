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


def experiment(data, folder):
    lambda1 = float(data['lambda1'])
    lambda2 = float(data['lambda1'])
    lambdad = float(data['lambdadelta'])
    freecad_file = os.path.join(folder, data['freecad_file'])
    PV_file = os.path.join(folder, data['PV_file'])

    logging.debug("in exp1", locals())
    destfile = folder + '.output'
    with io.open(destfile, 'w', encoding='utf8') as fp:
        string = u"parameters: {}, {}, {}, {}".format(lambda1, lambda2, lambdad, lambda2 - lambda1)
        fp.write(string)

    FreeCAD.openDocument(freecad_file)
    doc = FreeCAD.ActiveDocument

    raytrace.create_reflector_lambertian_layer("rlamb", 1.0)
    raytrace.create_two_layers_material("RLamb", "rlamb", "rlamb")

    file_Si = PV_file #'Perovs.txt'  # change for your path
    raytrace.create_PV_material("PV1", file_Si)

    sel = doc.Objects
    current_scene = raytrace.Scene(sel)
    phi_ini = 0 + 0.0000001
    phi_end = 0
    phi_end = phi_end + 0.00001
    phi_step = 0.1
    theta_ini = 0 + 0.0000001
    theta_end = 0
    theta_end = theta_end + 0.00001
    theta_step = 2
    number_of_rays = 10
    aperture_collector = 1. * 1. * 1.0
    lambda_ini = 295.0
    lambda_end = 810.5
    step_lambda = 0.5
    ##### data_file_spectrum = 'ASTMG173-direct.txt'
    # light_spectrum = raytrace.create_CDF_from_PDF(data_file_spectrum)
    # Buie_model = raytrace.BuieDistribution(0.05)
    Buie_model = None
    outfile = open(os.path.join(folder,'kkk4.txt'), 'w')
    outfile_PV = open(os.path.join(folder,'PV-10000-CAS4-kk.txt'), 'w')
    outfile_PV_values = open(os.path.join(folder,'PV_values_1micro.txt'), 'w')
    outfile_Source_lambdas = open(os.path.join(folder,'Source_lambdas_1micro.txt'), 'w')
    outfile_Source_lambdas.write("%s %s" % (aperture_collector * 0.001 * 0.001, "# Collector aperture in m2") + '\n')
    outfile_Source_lambdas.write("%s %s" % (number_of_rays, "# Rays per wavelength") + '\n')
    outfile_Source_lambdas.write("%s %s" % (step_lambda, "# Step of wavelength in nm") + '\n')

    Source_lambdas = []
    PV_energy = []
    PV_wavelength = []
    PV_values = []
    t0 = time.time()
    for ph in np.arange(phi_ini, phi_end, phi_step):
        #    for th in np.arange(theta_ini, theta_end, theta_step):
        for w in np.arange(lambda_ini, lambda_end, step_lambda):
            th = theta_ini
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
            print ("%s %s %s %s" % (w, th, efficiency, t1 - t0) + '\n')
            outfile.write("%s %s %s %s" % (ph, th, efficiency, t1 - t0) + '\n')
            PV_energy.append(exp.PV_energy)
            PV_wavelength.append(exp.PV_wavelength)
            PV_values.append(exp.PV_values)

    xarray = np.array(np.concatenate(PV_energy))
    yarray = np.array(np.concatenate(PV_wavelength))
    data = np.array([xarray, yarray])
    data = data.T
    data_PV_values = np.array(np.concatenate(PV_values))
    data_Source_lambdas = np.array(Source_lambdas)
    np.savetxt(outfile_PV, data, fmt=['%f', '%f'])
    np.savetxt(outfile_PV_values, data_PV_values, fmt=['%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f', '%f'])

    np.savetxt(outfile_Source_lambdas, data_Source_lambdas, fmt=['%f'])

    outfile.close()
    outfile_PV.close()
    outfile_PV_values.close()
    outfile_Source_lambdas.close()
    return outfile
