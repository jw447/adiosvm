#!/usr/bin/env python3
from __future__ import absolute_import, division, print_function, unicode_literals
import adios2
import argparse
from mpi4py import MPI
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import decomp
import time
import os


def SetupArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instream", "-i", help="Name of the input stream", required=True)
    parser.add_argument("--outfile", "-o", help="Name of the output file", default="screen")
    parser.add_argument("--varname", "-v", help="Name of variable read", default="U")
    parser.add_argument("--nompi", "-nompi", help="ADIOS was installed without MPI", action="store_true")
    parser.add_argument("--displaysec", "-dsec", help="Float representing gap between plot window refresh", default=0.1)
    parser.add_argument("--nx", "-nx", help="Integer representing process decomposition in the x direction",default=1)
    parser.add_argument("--ny", "-ny", help="Integer representing process decomposition in the y direction",default=1)
    parser.add_argument("--nz", "-nz", help="Integer representing process decomposition in the z direction",default=1)
    parser.add_argument("--plane", "-plane", help="The 2D plane to be displayed/stored xy/yz/xz/all", default='yz')
    args = parser.parse_args()

    args.displaysec = float(args.displaysec)
    args.nx = int(args.nx)
    args.ny = int(args.ny)
    args.nz = int(args.nz)

    if args.plane not in ('xz', 'yz', 'xy', 'all'):
        raise "Input argument --plane must be one of xz/yz/xy/all"

    return args

#def Write3D(data, args, fullshape, step):


def Plot2D(plane_direction, data, args, fullshape, step, fontsize):
    # Plotting part
    displaysec = args.displaysec
    gs = gridspec.GridSpec(1, 1)
    fig = plt.figure(1, figsize=(8,8))
    ax = fig.add_subplot(gs[0, 0])
    colorax = ax.imshow(data, origin='lower', interpolation='quadric',extent=[0, fullshape[1], 0, fullshape[0]], cmap=plt.get_cmap('gist_ncar'))
    cbar = fig.colorbar(colorax, orientation='horizontal')
    cbar.ax.tick_params(labelsize=fontsize-4)

    for i in range(args.ny):
        y = fullshape[0] / args.ny * i
        ax.plot([0, fullshape[1]], [y, y], color='black')

    for i in range(args.nx):
        x = fullshape[1] / args.nx * i
        ax.plot([x, x], [0, fullshape[0]], color='black')

    ax.set_title("{0}, {1} plane, step {2}".format(args.varname, plane_direction, step), fontsize=fontsize)
    ax.set_xlabel(plane_direction[0], fontsize=fontsize)
    ax.set_ylabel(plane_direction[1], fontsize=fontsize)
    plt.tick_params(labelsize = fontsize-8)
    plt.ion()
    if (args.outfile == "screen"):
        plt.show()
        plt.pause(displaysec)
    elif args.outfile.endswith(".bp"):
        if step == 0:
            global adios
            global ioWriter
            global var
            global writer
            adios = adios2.ADIOS(mpi.comm_app)
            ioWriter = adios.DeclareIO("VizOutput")
            var = ioWriter.DefineVariable(args.varname, data.shape, [0,0], data.shape, adios2.ConstantDims, data)
            writer = ioWriter.Open(args.outfile, adios2.Mode.Write)

        writer.BeginStep()
        writer.Put(var, data, adios2.Mode.Sync)
        writer.EndStep()
    else:
        imgfile = args.outfile+"{0:0>5}".format(step)+"_" + plane_direction + ".png"
        fig.savefig(imgfile)

    plt.clf()


def read_data(args, fr, start_coord, size_dims):

    var1 = args.varname
    data= fr.read(var1, start_coord, size_dims )
    data = np.squeeze(data)
    return data


if __name__ == "__main__":

    args = SetupArgs()
#    print(args)

    # Setup up 2D communicators if MPI is installed
    mpi = decomp.MPISetup(args, 3)
    myrank = mpi.rank['app']

    # Read the data from this object
    fr = adios2.open(args.instream, "r", mpi.comm_app,"adios2.xml", "SimulationOutput")
#    vars_info = fr.availablevariables()


    # Get the ADIOS selections -- equally partition the data if parallelization is requested


    # Read through the steps, one at a time
    plot_step = 0
    for fr_step in fr:
#        if fr_step.current_step()
        start, size, fullshape = mpi.Partition_3D_3D(fr, args)
        cur_step= fr_step.current_step()
        vars_info = fr.available_variables()
#        print (vars_info)
        shape3_str = vars_info[args.varname]["Shape"].split(',')
        shape3 = list(map(int,shape3_str))
        sim_step = fr_step.read("step")

        if myrank == 0:
            print("GS Plot step {0} processing simulation output step {1} or computation step {2}".format(plot_step,cur_step, sim_step), flush=True)
#            if cur_step == 0:
#                print("Variable" + pdfvar + " shape is {" + vars_info[pdfvar]["Shape"]+"}")

        if args.plane in ('xy', 'all'):
            data = read_data (args, fr_step, [0,0,int(shape3[2]/2)], [shape3[0],shape3[1],1])
            Plot2D ('xy', data, args, fullshape, sim_step, fontsize)

        if args.plane in ('xz', 'all'):
            data = read_data (args, fr_step, [0,int(shape3[1]/2),0], [shape3[0],1,shape3[2]])
            Plot2D ('xz', data, args, fullshape, sim_step, fontsize)

        if args.plane in ('yz', 'all'):
            data = read_data (args, fr_step, [int(shape3[0]/2),0,0], [1,shape3[1],shape3[2]])
            Plot2D ('yz',  data, args, fullshape, sim_step, fontsize)
        plot_step = plot_step + 1;

    fr.close()

