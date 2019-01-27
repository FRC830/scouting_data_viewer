# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 10:48:55 2018

@author: rober
"""

from html.parser import HTMLParser

class Node:
    def __init__(self, tag, attributes, children=None):
        self.tag = tag
        self.attributes = attributes
        self.children = [] if children == None else children
    
    def __str__(self):
        return self._in_str()
    
    def _in_str(self, level=0):
        """Return a string representation of self, indented level times."""
        if self in self.children:
            print('CIRCLE')
            print('\t'*level + self.tag + ' ' + str(self.attributes))
            assert False
        result = '\t'*level + self.tag + ' ' + str(self.attributes)
        for child in self.children:
            if type(child) is type(self):
                result += '\n' + child._in_str(level=level+1)
            else:
                result += '\n' + '\t'*(level+1) + str(child)
        return result

def attrs_to_dict(attrs):
    """
    Return the given attrs, converted to a dict.
    
    Parameters:
        attrs: The attrs list to convert to a dict.
    """
    result = {}
    for key, val in attrs:
        result[key] = val
    return result

class TreeParser(HTMLParser):
    def __init__(self):
        super(TreeParser, self).__init__()
        
        self.stack = [Node('root', [])]
    
    def handle_starttag(self, tag, attrs):
#        print('Start ' + tag)
        node = Node(tag, attrs_to_dict(attrs))
        self.stack[-1].children.append(node)
        self.stack.append(node)
    
    def handle_endtag(self, tag):
#        print('End ' + tag)
        if tag != self.stack[-1].tag:
            raise AssertionError('tag: ' + tag +  ', current tag: ' + self.stack[-1].tag)
        
        self.stack = self.stack[:-1] #pop top
    
    def handle_data(self, data):
        if type(data) is str:
            if len(data) > 0:
                for line in data.splitlines():
                    if len(line) > 0:
                        self.stack[-1].children.append(line)
        else:
            self.stack[-1].children.append(data)

def parse(html):
    """
    Return the html, parsed.
    
    Parameters:
        html: The html to parse.
    """
    parser = TreeParser()
    parser.feed(html)
    return parser.stack[0].children