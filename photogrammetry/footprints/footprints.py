# -*- coding: utf-8 -*-

import math
import re
import httplib2, urllib
import json

import shapefile

def _gons2rad(gons):

    return math.pi * gons / 200.00

def _rotation_matrix(omega, phi, kappa):


    o = _gons2rad(omega)
    p = _gons2rad(phi)
    k = _gons2rad(kappa)

    #~ o = omega
    #~ p = phi
    #~ k = kappa
    
    cos = math.cos
    sin = math.sin
    
    m11 = cos(p) * cos(k)
    m12 = sin(o) * sin(p) * cos(k) + cos(o) * sin(k)
    m13 = - cos(o) * sin(p) * cos(k) + sin(o) * sin(k)
    m21 = - cos(p) * sin(k)
    m22 = - sin(o) * sin(p) * sin(k) + cos(o) * cos (k)
    m23 = cos(o) * sin(p) * sin(k) + sin(o) * cos(k)
    m31 = sin(p)
    m32 = - sin(o) * cos(p)
    m33 = cos(o) * cos(p)
    
    return {
        'm11': m11,
        'm12': m12,
        'm13': m13,
        'm21': m21,
        'm22': m22,
        'm23': m23,
        'm31': m31,
        'm32': m32,
        'm33': m33,
    }
    
def _parse_orientation(file_):
    
    f = open(file_)
    
    header = False

    list_ = []
    header_ = []

    for line in f:
        
        if len(line) > 2:
            if header:
                list_.append(line.split())
            else:
                header_ = line.split('><')
            
            header = True

    f.close()

    for idx, val in enumerate(header_):
        pattern = re.sub(r'[^a-zA-Z0-9]','', val) 
        header_[idx] = pattern.lower()

    return header_, list_


def _img_coordinates(camera):
    
    half_longtrack = camera['long_track'] / 2
    half_crosstrack = camera['cross_track'] / 2
    
    xy1 = [
        - half_longtrack * camera['pixel_long_track'] / 1000,
        half_crosstrack * camera['pixel_cross_track'] / 1000
    ]

    xy2 = [
        - half_longtrack * camera['pixel_long_track'] / 1000,
        - half_crosstrack * camera['pixel_cross_track'] / 1000
    ]

    xy3 = [
        half_longtrack * camera['pixel_long_track'] / 1000,
        - half_crosstrack * camera['pixel_cross_track'] / 1000
    ]

    xy4 = [
        half_longtrack * camera['pixel_long_track'] / 1000,
        half_crosstrack * camera['pixel_cross_track'] / 1000
    ]
    
    return [xy1, xy2, xy3, xy4]

def _altimetry_webservice(x, y, url_params):
    
    url = url_params['url']
    
    params = {}
    
    for key, val in url_params['params'].items():
        
        if key == 'x':
            params[val] = x - 2000000
        elif key == 'y':
            params[val] = y - 1000000
        else:
            params[key] = val

    params=urllib.urlencode(params)
    
    url += '?'+params
    
    http = httplib2.Http()
    

    resp, content = http.request(
        url, method='GET'
    )
    
    content = json.loads(content)
    
    return content['mnt']

def compute_footprints(file_, output, camera, url_altimetry_params = None):
    
    header, data = _parse_orientation(file_)
    print header
    omega_position = header.index('omega')
    phi_position = header.index('phi')
    kappa_position = header.index('kappa')
    x_position = header.index('easting')
    y_position = header.index('northing')
    z_position = header.index('height')
    id_position = header.index('photoid')
    
    x0 = camera['X_ppa']
    y0 = camera['Y_ppa']
    f = camera['focal']

    for line in data:
        
        XYs = _img_coordinates(
            camera
        )
        
        print XYs

        m = _rotation_matrix(
            float(line[omega_position]),
            float(line[phi_position]),
            float(line[kappa_position])
        )
        
        z = _altimetry_webservice(
            float(line[x_position]),
            float(line[y_position]), 
            url_altimetry_params
        )
        
        w = shapefile.Writer(shapefile.POINT)
        w.point(float(line[x_position]),float(line[y_position]))
        w.field('FIRST_FLD','C','40')
        w.record('First')
        w.save('C:/travail/img/point')
        Dz = (z - float(line[z_position])) #mm
        
        print m

        w = shapefile.Writer(shapefile.POLYGON)
        
        part = []
#~ >>> w.poly(parts=[[[1,5],[5,5],[5,1],[3,3],[1,1]]])
#~ >>> w.field('FIRST_FLD','C','40')
#~ >>> w.field('SECOND_FLD','C','40')
#~ >>> w.record('First','Polygon')
#~ >>> w.save('shapefiles/test/polygon')

        first = True

        for xy in XYs:
            
            up = m['m11'] * (xy[0] -x0) + m['m21'] * (xy[1] - y0 + m['m31'] * (-f))
            down = m['m13'] * (xy[0] -x0) + m['m23'] * (xy[1] - y0 + m['m33'] * (-f))
            
            xM = up / down
            
            up = m['m12'] * (xy[0] -x0) + m['m22'] * (xy[1] - y0 + m['m32'] * (-f))
            down = m['m13'] * (xy[0] -x0) + m['m23'] * (xy[1] - y0 + m['m33'] * (-f))
            
            yM = up / down
        
            print 'Dz:'+str(Dz)
            Dx = Dz * xM
            Dy = Dz * yM
            
            x = float(line[x_position]) + Dx / 1000
            y = float(line[y_position]) + Dy / 1000

            print 'Dx: '+str(Dx)
            print 'XL:'+str(line[x_position])
            print 'X:'+str(x)            
            print 'YL:'+str(line[y_position])
            print 'Y:'+str(y)
            
            part.append([x, y])
            
            if first is True:
                last_part = [x, y]
                first = False

        w.poly(parts=[part])
        w.field('IMAGE_ID','C','40')
        w.record(line[id_position])
        
        w.save('C:/travail/img/polygon')
        asd
    print header
    
        
    
    
    return None
    


file_ = "C:/travail/img/LaChauxdeFonds_LV95_LHN95_xyz_360.dat"

camera = {
    'long_track': 11310,
    'cross_track': 17310,
    'pixel_long_track': 6.000,
    'pixel_cross_track': 6.000,
    'focal': 100.500,
    'X_ppa': 0.000,
    'Y_ppa': 0.120
}

url = {
    'url': "http://sitn.ne.ch/production/wsgi/raster",
    'params': {
        'layers': 'mnt',
        'x': 'lon',
        'y': 'lat'
    }
}


compute_footprints(file_, 'toto', camera, url_altimetry_params = url)