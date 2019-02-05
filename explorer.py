import os
import sys
import re
import pandas as pd
import argparse

out_folder = './stdout/'
cfg_folder = './configs/'

layer = re.compile('Commencing run for (.*)')
cyc = re.compile('Cycles for compute  :\s+(\d+)\s+cycles')
ifbw = re.compile('DRAM IFMAP Read BW  :\s+(\d+\.\d+)\s+Bytes/cycle')
filbw = re.compile('DRAM Filter Read BW :\s+(\d+\.\d+)\s+Bytes/cycle')
ofbw = re.compile('DRAM OFMAP Write BW :\s+(\d+\.\d+)\s+Bytes/cycle')

def write_config(run_type = "mobile", array_height = 32, array_width = 32, ifmap_sz = 1024, filter_sz = 1024, ofmap_sz = 2048, cfg_file = 'test.cfg'):
    cfg_string = '[general]\nrun_name = "lab2_%s"\n\n[architecture_presets]\nArrayHeight:   %d\nArrayWidth:    %d\nIfmapSramSz:   %d\nFilterSramSz:   %d\nOfmapSramSz:    %d\nIfmapOffset:    0\nFilterOffset:   10000000\nOfmapOffset: 20000000\nDataflow:       ws' % (run_type, array_height, array_width, ifmap_sz, filter_sz, ofmap_sz)
    cfg_path = cfg_folder + cfg_file
    cfg_out = open(cfg_path, 'w')
    cfg_out.write(cfg_string)
    cfg_out.close
    print(cfg_string)
    return cfg_path

def run_test(out_file='./stdout/out_latest.txt', cfg_path='./configs/lab2.cfg'):
    os.system('python scale.py -arch_config=%s -network=../Lab2/ece8893_lab2.csv > %s' % (cfg_path, out_file))
    return out_file

def check_constraints(max_bw_csv):
    max_bw = pd.read_csv(max_bw_csv)
    max_val = 0.0
    bws = ['\tMax DRAM IFMAP Read BW', '\tMax DRAM Filter Read BW', '\tMax DRAM OFMAP Write BW']
    for bw in bws:
        for val in max_bw[bw]:
            if val > max_val:
                max_val = val
            if float(val) > 20.0:
                print("Max BW exceeded: %s = %f" %(bw, val))
                return False
    print("Max BW: %f" % max_val)
    return True

def get_cost(out_path=None):
    cost = 0.0
    output_fh = open(out_path,'r')
    for line in output_fh:
        m_layer = layer.match(line)
        if m_layer:
            d_layer = m_layer.group(1)
        m_cyc = cyc.match(line)
        if m_cyc:
            d_cyc = float(m_cyc.group(1))
        m_ifbw = ifbw.match(line)
        if m_ifbw:
            d_ifbw = float(m_ifbw.group(1))
        m_filbw = filbw.match(line)
        if m_filbw:
            d_filbw = float(m_filbw.group(1))
        m_ofbw = ofbw.match(line)
        if m_ofbw:
            d_ofbw = float(m_ofbw.group(1))
            cost = cost + (d_cyc * (d_ifbw + d_filbw + d_ofbw))
    return cost

def check_cost(cost):
    try:
        prevcost = open('/tmp/prevcost','r')
        p_cost = float(prevcost.readline())
        prevcost.close
    except:
        p_cost = -1.0

    prevcost = open('/tmp/prevcost','w')
    prevcost.write(str(cost))
    prevcost.close

    if p_cost > 1:
        cost_diff = cost - p_cost
        print("CostDiff: %f" % cost_diff)
        if cost_diff > 0:
            print("Cost increased!")
            return False
        elif cost_diff == 0:
            print("No Change!")
            return True
        else:
            print("Cost decreased!")
            return True


def main(in_run_type, in_array_height, in_array_width, in_ifmap_sz, in_filter_sz, in_ofmap_sz, in_cfg_file, out_file):
    cfg_path = write_config(run_type = in_run_type, array_height = in_array_height, array_width = in_array_width, ifmap_sz = in_ifmap_sz, filter_sz = in_filter_sz, ofmap_sz = in_ofmap_sz, cfg_file = in_cfg_file)
    out_path = run_test(out_file=out_folder+out_file, cfg_path=cfg_path)
    cost = get_cost(out_path)    
    check_constraints('./outputs/lab2_%s/ece8893_lab2_max_bw.csv' % in_run_type)
    print("Cost: %s" % str(cost))
    check_cost(cost)

  
if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Explore ScaleSIM design choices!')
    parser.add_argument('-rt','--run_type', default = "mobile", type=str, help='')
    parser.add_argument('-ht','--array_height', default = 32, type=int, help='')
    parser.add_argument('-wt','--array_width', default = 32, type=int, help='')
    parser.add_argument('-if','--ifmap_sz', default = 2048, type=int, help='')
    parser.add_argument('-fs','--filter_sz', default = 1024, type=int, help='')
    parser.add_argument('-of','--ofmap_sz', default = 2048, type=int, help='')
    parser.add_argument('-cfg','--cfg_file', default = 'test.cfg', type=str, help='')
    parser.add_argument('-out','--out_file', default = 'test.txt', type=str, help='')
    args = parser.parse_args()
    main(in_run_type=args.run_type, in_array_height=args.array_height, in_array_width=args.array_width, in_ifmap_sz=args.ifmap_sz, in_filter_sz=args.filter_sz, in_ofmap_sz=args.ofmap_sz, in_cfg_file=args.cfg_file, out_file=args.out_file)



