from mathutils import *
from math import *
import numpy as np
import bpy


def vec2str(vec):
    return "x=" + str(vec.x) + ",y=" + str(vec.y) + ",z=" + str(vec.z)

def cross_product(v1, v2):
    return Vector((v1.y*v2.z-v1.z*v2.y, v1.z*v2.x-v1.x*v2.z, v1.x*v2.y-v1.y*v2.x))

def vector_length(v):
    return sqrt(v.x*v.x + v.y*v.y + v.z*v.z)

def normalize(v):
    return v/vector_length(v)

def dot_product(v1, v2):
    return v1.x*v2.x+v1.y*v2.y+v1.z*v2.z

def included_angle(v1, v2):
    return np.arccos(dot_product(v1,v2)/(vector_length(v1)*vector_length(v2)))

def GammaToLinearSpaceExact(value):
    if value <= 0.04045:
        return value / 12.92
    elif value < 1.0:
        return pow((value + 0.055)/1.055, 2.4)
    else:
        return pow(value, 2.2)

def GammaToLinearSpace(color):
    return [GammaToLinearSpaceExact(color[0]), GammaToLinearSpaceExact(color[1]), GammaToLinearSpaceExact(color[2]), color[3]]



me = bpy.data.meshes['布洛妮娅']
me.calc_tangents(uvmap = "UVMap")
dict = {}

def need_outline(vertex):
    need = True
    return need

for v in me.vertices:
    co = v.co
    co_str = vec2str(co)
    dict[co_str] = []

for poly in me.polygons:
    l0 = me.loops[poly.loop_start]
    l1 = me.loops[poly.loop_start + 1]
    l2 = me.loops[poly.loop_start + 2]
    
    v0 = me.vertices[l0.vertex_index]
    v1 = me.vertices[l1.vertex_index]
    v2 = me.vertices[l2.vertex_index]
    
    n = cross_product(v1.co - v0.co, v2.co - v0.co)
    if vector_length(n) == 0:
        continue
    n = normalize(n)
    
    co0_str = vec2str(v0.co)
    co1_str = vec2str(v1.co)
    co2_str = vec2str(v2.co)
    
    if co0_str in dict:
        w = included_angle(v2.co - v0.co, v1.co - v0.co)
        dict[co0_str].append({"n":n, "w":w, "l":l0})
    if co1_str in dict:
        w = included_angle(v0.co - v1.co, v2.co - v1.co)
        dict[co1_str].append({"n":n, "w":w, "l":l1})
    if co2_str in dict:
        w = included_angle(v1.co - v2.co, v0.co - v2.co)
        dict[co2_str].append({"n":n, "w":w, "l":l2})
        
        
for poly in me.polygons:
    for loop_index in range(poly.loop_start, poly.loop_start + poly.loop_total):
        vertex_index = me.loops[loop_index].vertex_index
        v = me.vertices[vertex_index]
        smoothnormal = Vector((0, 0, 0))
        weightsum = 0
        alpha = 1
        if need_outline(v):
            costr = vec2str(v.co)
            if costr in dict:
                a = dict[costr]
                for d in a:
                    n = d['n']
                    w = d['w']
                    smoothnormal += n * w
                    weightsum += w;
                    print(costr + " : "+ str(w))
        if smoothnormal != Vector((0, 0, 0)):
            smoothnormal /= weightsum
            smoothnormal = normalize(smoothnormal)
        
        normal = me.loops[loop_index].normal    
        tangent = me.loops[loop_index].tangent    
        bitangent = me.loops[loop_index].bitangent    
        
        normalTSX = dot_product(tangent, smoothnormal);
        normalTSY = dot_product(bitangent, smoothnormal);
        normalTSZ = dot_product(normal, smoothnormal);
        
        normalTS = Vector((normalTSX, normalTSY, normalTSZ))
        color = [normalTS.x * 0.5 + 0.5, normalTS.y * 0.5 + 0.5 , normalTS.z * 0.5 + 0.5, alpha]
        color = GammaToLinearSpace(color)
        me.color_attributes[0].data[loop_index].color = color