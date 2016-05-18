# -*- coding: UTF-8 -*-
"""
FileName: transform.py
=============================================================================
Converts EPSG:4326 (WGS84) latitude and longitude to Easting/Northing 
coordinates in EPSG:2056

This was done regarding the rigorous approach described in this paper:
http://www.swisstopo.admin.ch/internet/swisstopo/fr/home/topics/survey/sys/refsys/switzerland.parsysrelated1.31216.downloadList.63873.DownloadFile.tmp/swissprojectionfr.pdf
(last accessed 2016/05/18)
=============================================================================

Created: [2016/05/18]
Author: Michael Kalbermatten
"""

import math
import logging


def mn95wgs84(easting, northing):

    FORMAT = "%(levelname)s: %(message)s"    
    logging.basicConfig(level=logging.INFO, format=FORMAT)
    
    # Step 3.3
    # Constants:
    r = 6378815.90365
    b0 = math.radians(46.0 + 54.0/60.0 + 27.83324844/3600.0)
    alpha = 1.00072913843038   
    lon0 = 7.0 + 26.0/60.0 + 22.5/3600.0
    lon0 = math.radians(lon0)
    k = 0.0030667323772751
    e2 =0.006674372230614
    e = math.sqrt(e2)
    
    y = easting - 2600000.0
    x = northing - 1200000.0

    l_ = y / r
    b_ = 2 * (math.atan(math.exp(x/r)) - math.pi/4)
    
    b = math.asin(math.cos(b0)*math.sin(b_) + math.sin(b0)*math.cos(b_)*math.cos(l_))
    l = math.atan(math.sin(l_)/(math.cos(b0)*math.cos(l_) - math.sin(b0)*math.tan(b_)))
    
    lambda_ = lon0 + l/alpha
    
    phi = b
    s0 = (math.log(math.tan(math.pi/4 + b /2)) -k ) / alpha

    count = 0
    delta = 10000
    while delta != 0.0:
        
        s1 = e * math.log(math.tan(math.pi/4 + math.asin(e*math.sin(phi))/2))
        s = s0 + s1
        phi_new = 2*math.atan(math.exp(s)) - math.pi/2
        delta = phi - phi_new
        #~ print delta
        phi = phi_new
        #~ print 'The count is:', count
        count += count
        if count > 1000:
            logging.info('Solution did not converge')
            sys.exit(1)
            break

    # Step 2.1
    a = 6377397.155
    rn = a / math.sqrt(1 - e2*math.sin(phi)*math.sin(phi))
    h = 0.0
    X = (rn + h) * math.cos(phi) * math.cos(lambda_)
    Y = (rn + h) * math.cos(phi) * math.sin(lambda_)
    Z = (rn * (1 - e2) + h) * math.sin(phi)

    # Step 1.4
    x_chtrs95 = X + 674.374
    y_chtrs95 = Y + 15.056
    z_chtrs95 = Z + 405.346

    #Step 2.2   
    lambda_ = math.atan(y_chtrs95/x_chtrs95)
    
    # Constant (GRS 80 ellipsoid)
    a = 6378137.000
    e2 = 0.006694380023011
    
    phi = math.atan(z_chtrs95 / math.sqrt(x_chtrs95*x_chtrs95+y_chtrs95*y_chtrs95))

    count = 0
    delta = 10000
    while delta != 0.0:
        
        x2_y2 = math.sqrt(x_chtrs95*x_chtrs95 + y_chtrs95*y_chtrs95)
        
        rn = a / math.sqrt(1 - e2*math.sin(phi)*math.sin(phi))

        h = (x2_y2 / math.cos(phi)) - rn
        
        numerator = z_chtrs95 / x2_y2
    
        denominator = (1-((rn*e2)/(rn+h)))
        
        
        phi_new = math.atan(numerator / denominator)
        delta = phi - phi_new

        phi = phi_new

        count = count + 1
        if count > 1000:
            logging.info('Solution did not converge')
            sys.exit(1)
            break

    lon = math.degrees(lambda_)
    lat = math.degrees(phi)

    return lon, lat


def wgs84mn95(easting, northing):

    FORMAT = "%(levelname)s: %(message)s"    
    logging.basicConfig(level=logging.INFO, format=FORMAT)

    easting = math.radians(easting)
    northing = math.radians(northing)

    # 2.1 (GRS 80 ellipsoid)
    a = 6378137.000
    e2 = 0.006694380023011
    h = 0
    rn = a / math.sqrt(1-e2*math.sin(northing)*math.sin(northing))
    
    X = (rn+h)*math.cos(northing)*math.cos(easting)
    Y = (rn+h)*math.cos(northing)*math.sin(easting)
    Z = (rn*(1-e2)+h)*math.sin(northing)

    # 1.4
    X03plus = X - 674.374
    Y03plus = Y - 15.056
    Z03plus = Z - 405.346
    
    # 2.2 (Bessel 1841 ellispoid)
    e2 = 0.006674372230614
    a = 6377397.155
    
    lambda_ = math.atan(Y03plus/X03plus)

    phi = math.atan(Z03plus / math.sqrt(X03plus*X03plus + Y03plus*Y03plus))

    count = 0
    delta = 10000
    while delta != 0.0:
        
        x2_y2 = math.sqrt(X03plus*X03plus + Y03plus*Y03plus)
        
        rn = a / math.sqrt(1 - e2*math.sin(phi)*math.sin(phi))

        h = (x2_y2 / math.cos(phi)) - rn
        
        numerator = Z03plus / x2_y2
    
        denominator = 1 - ((rn*e2) / (rn + h))
        
        
        phi_new = math.atan(numerator/denominator)
        
        delta = phi - phi_new
        phi = phi_new

        count += 1
        if count > 1000:
            logging.info('Solution did not converge')
            sys.exit(1)
            break
    
    easting = lambda_
    northing = phi
    
    e2 =0.006674372230614
    e = math.sqrt(e2)
    lon0 = 7.0 + 26.0/60.0 + 22.5/3600.0
    lon0 = math.radians(lon0)
    lat0 = 46.0 + 57.0/60.0 + 8.66/3600.0
    lat0 = math.radians(lat0)
    
    rr2 = a * math.sqrt(1 - e2) / (1 - e2*math.sin(lat0) * math.sin(lat0))
    
    rr = 6378815.90365
    alpha = 1.00072913843038   
    b0 = math.radians(46.0 + 54.0/60.0 + 27.83324844/3600.0)
    
    k = 0.0030667323772751
    
    s = alpha * math.log( math.tan(math.pi/4 + northing/2))
    s = s - alpha * e/2 * math.log((1 + e*math.sin(northing)) / (1 - e*math.sin(northing))) + k 

    lat_sph = 2 * (math.atan(math.exp(s)) - math.pi/4)
    lon_sph = alpha*(easting - lon0)
    
    l_ = math.atan(math.sin(lon_sph)/(math.sin(b0)*math.tan(lat_sph)+math.cos(b0)*math.cos(lon_sph)))
    b_ = math.asin(math.cos(b0)*math.sin(lat_sph) - math.sin(b0)*math.cos(lat_sph)*math.cos(lon_sph))
    
    Y = rr * l_
    X = rr / 2 * math.log((1 + math.sin(b_)) / (1-math.sin(b_)))
    

    y_95 = Y + 2600000
    x_95 = X + 1200000

    return y_95, x_95
