# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 15:03:12 2018

@author: rober
"""

import pickle as pkl

import encode as ec

high = 99999999

def get_code(): #Write the easter egg code
    file = open('easter_eggs_text.txt')
    code = list(file)
    code = ''.join(code)#List of chars -> string
    encoded = ec.h_encode(code, high=high)
    write_to = open('encoded.txt', 'wb')
    pkl.dump(encoded, write_to)
get_code()