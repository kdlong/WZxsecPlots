#!/usr/bin/env python
import plot_functions as plotter
import argparse
import ROOT
import config_object

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root_file", type=str, required=True,
                        help="Name of root file where plots are stored")
    parser.add_argument("-o", "--output_file", type=str, required=True,
                        help="Name of file to be created (type pdf/png etc.)")
    parser.add_argument("-n", "--cutflow_name", type=str, required=False,
                        help="Name of cut flow in cutflow.json config file")
    return parser.parse_args()
def getCutFlowHist(root_file_name, config, name_in_config):
    root_file = ROOT.TFile(root_file_name)                          
    cutflow_hist = plotter.getHistFromFile(root_file, "cutflow", 
                                           name_in_config, "")                                                                  
    cutflow_hist.Draw()
    config.setAttributes(cutflow_hist, name_in_config)
    return cutflow_hist

def stackFromConfig(config, root_file_name):
    hist_stack = ROOT.THStack("cutflow stack", "cutflow stack")
    for hist_name in config.getListOfHists():
        
        hist = getCutFlowHist(
            root_file_name.replace(".", hist_name.replace("cutflow", "") + "."), 
            config,
            hist_name)
        hist_stack.Add(hist)
    print root_file_name.replace(".", hist_name.replace("cutflow", "") + "."), 
    return hist_stack
def main():
    args = getComLineArgs()
    config_file = "/cms/kdlong/WZxsec/InitialStateAnalysis/" \
                  "my_plotting/config_files/cutflows.json"
    config = config_object.ConfigObject(config_file)
    canvas = config.getCanvas()
    if args.cutflow_name is not None:
    
        hist = getCutFlowHist(args.root_file, config,  args.cutflow_name)                                                                                                                         
    else:
        hist_stack = stackFromConfig(config, args.root_file)
        hist_stack.Draw("nostack")
    
    canvas.Print(args.output_file)                                                                                       

if __name__ == "__main__":
    main()
