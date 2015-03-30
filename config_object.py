#!/usr/bin/env python
import argparse
import ROOT
import json

class ConfigObject:
    def __init__(self, config_file):
        with open(config_file) as json_file:    
            self.data = json.load(json_file)
                
    def getObject(self, object_name):
        initialize = self.data[object_name]['Initialize']
        if "TH1" in initialize['type']:
            tObject = ROOT.TH1F(object_name, object_name, 
                            initialize['nbins'], initialize['xmin'], 
                            initialize['xmax'])
            tObject.SetDirectory(ROOT.gROOT)
        elif initialize['type'] == "TCanvas":
            tObject = ROOT.TCanvas(object_name, object_name, 
                                initialize['ww'], initialize['wh'])
        else:
            tObject = ""
        return tObject
    def deepGetattr(self, obj, attr):
        """Recurses through an attribute chain to get the ultimate value.
            via http://pingfive.typepad.com/blog/2010/04/deep-getattr-python-function.html"""
        return self.evaluateNested(getattr, attr.split('.'), obj)
    def evaluateNested(self, func, iterable, start=None):
        it = iter(iterable)
        if start is None:
            try:
                start = next(it)
            except StopIteration:
                raise TypeError('reduce() of empty sequence with no initial value')
        accum_value = start
        for x in iterable:
            evaluate = False
            if "(" in x:
                x = x.replace("()", "")
                evaluate = True
            accum_value = func(accum_value, x)
            if evaluate:
                accum_value = accum_value()
        return accum_value

    def setAttributes(self, tObject, object_name):
        functions = []
        attributes =  self.data[object_name]['Attributes']
        print attributes
        for function_call, params in attributes.iteritems():
            if not isinstance(params, list): 
                params = [params]
            parsed_params = []
            for param in params:
                param_str = str(param)
                if "ROOT" in param_str:
                    expr = param_str.replace("ROOT.", "")
                    if "+" in param_str:
                        values = [x.strip() for x in expr.split("+")]
                        root_val = self.deepGetattr(ROOT, values[0])
                        root_val += int(values[1]) 
                    elif "-" in param_str:
                        values = [x.strip() for x in expr.split("-")]
                        root_val =self.deepGetattr(ROOT, values[0])
                        root_val -= int(values[1]) 
                    else:
                        root_val =self.deepGetattr(ROOT, expr)
                    param = root_val
                    
                parsed_params.append(param)
            self.deepGetattr(tObject, function_call)(*parsed_params)
    def getHistCanvas(self, hist_name):
        canvas = getCanvas(self)
        hist = self.getObject(hist_name) 
        hist.Draw()
        self.setAtrributes(hist)
        hist.Draw()
        return canvas
    def getCanvas(self):
        canvas = self.getObject("Canvas") 
        self.setAttributes(canvas, "Canvas")
        canvas.cd()
        return canvas
    def getListOfHists(self):
        list_of_hists = []
        for key in self.data:
            if key != "Canvas":
                list_of_hists.append(key)
        print list_of_hists
        return list_of_hists
