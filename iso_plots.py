#!/usr/bin/env python
import plot_functions as plotter
import config_object
import argparse
import ROOT
import os
import sys

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_file", type=str, required=True,
                        help="Name of root file where plots are stored")
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("-t", "--path_to_tree", type=str, required=True,
                        help="Full path to tree (e.g. ")
    parser.add_argument("-l", "--lepton_nums", type=int, required=True,
                        nargs='+', help="Number of leptons to plot"
                        " call as ex. -l 1 3")
    parser.add_argument("--combine", action='store_true', help="Plot all"
                        " leptons specified by --lepton_nums in the same "
                        " histogram")
    parser.add_argument("-e", "--eiso_cut", type=float, default=0,
                        required=False, help="Cut on electron isolation")
    parser.add_argument("-m", "--miso_cut", type=float, default=0,
                        required=False, help="Cut on muon isolation")
    return parser.parse_args() 

def printHist(hist, canvas, output_file_name, cwd):        
        hist.Draw()
        os.chdir(cwd)
        canvas.Print(output_file_name)
        hist.Delete()

def plotOverflow(hist):
    # Returns num bins + overflow + underflow
    num_bins = hist.GetSize() - 2
    add_overflow = hist.GetBinContent(num_bins) + hist.GetBinContent(num_bins + 1)
    hist.SetBinContent(num_bins, add_overflow)

def main(): 
    args = getComLineArgs()
    root_file = ROOT.TFile(args.root_file)                          
    print root_file 
    cwd = os.getcwd()
    os.chdir(sys.path[0])
    
    eiso_cut = " && l%i.Iso < " + str(args.eiso_cut) if args.eiso_cut != 0 else ""
    miso_cut = " && l%i.Iso < " + str(args.miso_cut) if args.miso_cut != 0 else ""
    info = {'name' : "iso_%s",
            'branch' : "l%i.Iso",
            'cut_string' : "l%iFlv==\"%s\""
    } 
    config = config_object.ConfigObject("config_files/iso_all_hists.json")
    canvas = config.getCanvas()
    
    for lep in ["e", "m"]:
        name = info['name'].replace("_", "_all_" if args.combine else "_") % lep
        iso_hist = config.getObject(name)
        for i in args.lepton_nums:
            cut_string =  "".join([info['cut_string'] % (i, lep), ""])
                #(eiso_cut % i) if lep == "e" else (miso_cut % i)])
            print "The cut is %s" % cut_string
            plotter.loadHistFromTree(iso_hist, 
                root_file, 
                args.path_to_tree, 
                info['branch'] % i, 
                cut_string,
                args.combine if i != 1 else False)
            plotOverflow(iso_hist)
            config.setAttributes(iso_hist, name)
            if not args.combine:
                printHist(iso_hist, 
                    canvas,
                    args.output_file.replace(".", "_%s%i." % (lep, i)), 
                    cwd)
                iso_hist = config.getObject(name)
        if args.combine:
            printHist(iso_hist, 
                canvas,
                args.output_file.replace(".", "_%s_all." % lep), 
                cwd)

if __name__ == "__main__":
    main()
