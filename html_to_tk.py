# -*- coding: utf-8 -*-
"""
Created on Sun Jan 27 14:14:48 2019

@author: rober
"""

import tkinter as tk
import html_tree_parser

LAYOUT_ATTRIBUTES = ['fill', 'padx', 'ipadx', 'pady', 'ipady', 'side']

def make_gui_from_html(html_text, root=None, add_element=None, namespace=None):
    """
    Return a map from names to tkinter widgets, with the layout specified by the html.
    
    Parameters:
        html_text: The html specifying the gui,
        root: The root item to put the gui in. If none, a tk.Tk object.
        add_element: The function to call to add elements to the gui.
    
    Returns:
        A map from names (specified in 'name' attributes in HTML) to widgets 
    """
    namespace = namespace if namespace else {}
#    locals().update(namespace)#Put all the name-value mappings in namespace into the namespace
    root = root if root else tk.Tk()
    add_element = add_element if add_element else 'pack'
    html = html_tree_parser.parse(html_text)
    return make_gui_from_parsed_html(html, root=root, add_element=add_element, namespace=namespace)

def make_gui_from_html_file(file_name, root=None, add_element=None, namespace=None):
    html_text = ""
    with open(file_name) as file:
        for line in file:
            html_text += line
    return make_gui_from_html(html_text, root=root, add_element=add_element, namespace=namespace)

def make_gui_from_parsed_html(html, root=None, add_element=None, namespace=None):
    """
    Return a map from names to tkinter widgets, with the layout specified by the html.
    
    Parameters:
        html: The html specifying the gui.
        root: The root item to put the gui in. If none, a tk.Tk object.
        add_element: The function to call to add elements to the gui.
    
    Returns:
        A map from names (specified in 'name' attributes in HTML) to widgets 
    """
#    print('')
    root = root if root else tk.Tk()
    add_element = add_element if add_element else 'pack'
    namespace = namespace if namespace else {}
    result = {}
    for node in html:
#        print('Node: '+ str(node))
        w_result, w_namespace = make_widget_from_node(node, root=root, add_element=add_element, namespace=namespace)
        result.update(w_result)
        namespace.update(w_result)
        namespace.update(w_namespace)
    
    return result, namespace

LAYOUT_PREFIX = 'hl_'
SPECIAL_ATTRIBUTES = ['name', 'layout']

def capitalize_first(tag):
    return tag[0].upper() + tag[1:]

#def parse_val(val):
#    """
#    Parse the given val.
#    """
#    try: #Maybe it's an int
#        return int(val)
#    except ValueError: #It's a string
#        if val[0:3] == 'tk.':
#            return getattr(tk, val[3:])
#        else:
#            return val

def parse_val(val, namespace=None):
    namespace = namespace if namespace else {}
    locals().update(namespace)
#    print('val: ' + str(val))
    return eval(val)

def make_widget_from_node(node, root=None, add_element=None, namespace=None):
    """
    Return a widget made from the given node.
    
    Parameters:
        node: The node to make a widget from.
        root: The root to add the widget to.
        add_element: The function on the widget to call to layout the widget.
    """
    if type(node) is str:
        node = node.strip()
        if node:
            widget = tk.Label(root, text=node)
        return {}, {}
    
    namespace = namespace if namespace else {}
    
#    print(node.tag)
    
    if node.tag == 'exec':
#        if 'config_canvas' in namespace:
#            print(namespace['config_canvas'])
        locals().update(namespace)
        code = node.attributes.get('code', '')
        vals = list(locals())
        exec(code)
        new_vals = list(locals())
        added_vals = [val for val in new_vals if not val in vals]
        added_vals.remove('vals')
        new_namespace = {}
        for val in added_vals:
            new_namespace[val] = locals()[val]
        return {}, new_namespace
    
    widget_type = capitalize_first(node.tag)
    widget_class = getattr(tk, widget_type)
    widget_attributes = {}
    layout_attributes = {}
    
    for key in node.attributes:
        if not key in SPECIAL_ATTRIBUTES:
            val = parse_val(node.attributes[key], namespace=namespace)
            if key[0:3] == LAYOUT_PREFIX:
                layout_attributes[key[3:]] = val
            else:
                widget_attributes[key] = val
    
    
    widget = widget_class(root, **widget_attributes)
    if widget_type != 'Menu' and add_element != 'None':
#        print('adding to layout')
        getattr(widget, add_element)(**layout_attributes) #Add the element
    
    result = {}
#    print('namespace before: ' + str(namespace))
    if 'name' in node.attributes:
        name = node.attributes['name']
        result[name] = widget
        namespace[name] = widget
#    print('namespace after: ' + str(namespace))
    
    sub_add_element = node.attributes.get('layout', 'pack')
    h_result, h_namespace = make_gui_from_parsed_html(node.children, root=widget, add_element=sub_add_element, namespace=namespace)
    
    result.update(h_result)
    namespace.update(h_namespace)
    
    return result, {}