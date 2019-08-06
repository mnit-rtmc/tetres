# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from datetime import datetime

cases = [
    {
        'name' : '984',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 30,
        'k' : [37.312,18.186665,22.410667,13.493333,22.762667,18.538668,25.813332,23.701332,20.533333,34.26133,24.757334,17.6,28.16,29.333336,28.512,25.344,19.594667,20.298666,22.528,25.344,19.829334,22.293333,37.663998,21.002666,18.656,26.517334,30.976002,39.189335,38.250668,31.210667,28.629333,34.965336,24.053335,20.416,34.026665,26.4,20.533333,13.375999,28.16,46.229336,29.685335,24.288,23.701332,37.077335,38.250668,19.008001,21.472,34.026665,38.250668,40.48,39.541332,26.165335,32.618664,18.656,17.013332,20.768,33.674667,37.898666,19.008001,13.141333],
        'q' : [2640,1080,1680,960,1800,1440,2160,1920,1560,2160,1800,1320,1560,2040,2040,2040,1560,1560,1680,1800,1440,1800,2880,1320,1320,2040,1800,2520,2400,1920,2160,2640,1680,1560,2640,1920,1560,960,1800,2880,2040,1920,1440,2760,2280,1560,1440,2400,2400,2280,2520,2040,2400,1440,1320,1200,2520,2640,1320,1080],
        'o' : [17.666666,8.611111,10.611111,6.388889,10.777778,8.777778,12.222222,11.222222,9.722222,16.222221,11.722222,8.333333,13.333333,13.888889,13.5,12,9.277778,9.611111,10.666667,12,9.388889,10.555555,17.833334,9.944445,8.833333,12.555555,14.666667,18.555555,18.11111,14.777778,13.555555,16.555555,11.388889,9.666667,16.11111,12.5,9.722222,6.3333335,13.333333,21.88889,14.055555,11.5,11.222222,17.555555,18.11111,9,10.166667,16.11111,18.11111,19.166666,18.722221,12.388889,15.444445,8.833333,8.055555,9.833333,15.944445,17.944445,9,6.2222223],
        'u' : [70.75471698,59.38416966,74.9643016,71.14624682,79.07684983,77.67548348,83.67769027,81.00810537,75.97402721,63.04483801,72.70572833,75,55.39772727,69.54544822,71.54882155,80.49242424,79.61349892,76.85234094,74.57386364,71.02272727,72.61968556,80.741628,76.46559454,62.84916401,70.75471698,76.93081062,58.10950038,64.30320902,62.74400227,61.51742928,75.44709477,75.50334995,69.84478452,76.41065831,77.5862107,72.72727273,75.97402721,71.77034029,63.92045455,62.29810439,68.72080103,79.0513834,60.75607903,74.43900701,59.60680216,82.07070275,67.06408346,70.53291882,62.74400227,56.32411067,63.73078176,77.96575125,73.57750765,77.18696398,77.58621298,57.78120185,74.83370214,69.65944395,69.44444079,82.18344364],
        'v' : [22,9,14,8,15,12,18,16,13,18,15,11,13,17,17,17,13,13,14,15,12,15,24,11,11,17,15,21,20,16,18,22,14,13,22,16,13,8,15,24,17,16,12,23,19,13,12,20,20,19,21,17,20,12,11,10,21,22,11,9]
    },

    {
        'name' : '984',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 300,
        'k' : [23.70133,24.147198,28.558935,27.678934,30.624002,25.848532],
        'q' : [1740,1740,1944,1980,2052,1848],
        'o' : [11.222222,11.433333,13.522222,13.105556,14.5,12.238889],
        'u' : [73.41360168,72.05804997,68.06976521,71.53454681,67.00626522,71.49342175],
        'v' : [145,145,162,165,171,154],
    },

    {
        'name' : '475',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 30,
        'k' : [1.5894911,12.137931,3.4679804,8.525452,8.81445,3.4679804,8.380953,9.103449,3.7569788,10.837439,8.81445,5.0574718,8.669951,10.69294,7.224959,3.323481,8.669951,6.791462,10.259442,3.0344827,14.883417,10.259442,14.449918,8.525452,8.380953,6.935961,14.883417,8.81445,1.7339902,9.103449,2.0229883,14.16092,15.89491,11.993431,0,3.4679804,12.282431,17.195404,3.7569788,24.420364,8.236453,7.5139575,7.658457,5.34647,14.016421,5.635468,3.7569788,7.802956,9.825944,17.917898,18.062399,1.5894911,6.791462,11.704433,12.282431,3.323481,6.3579645,7.224959,10.981938,6.935961],
        'q' : [120,840,240,600,600,240,600,480,240,840,240,360,360,720,600,240,600,480,360,240,1080,720,840,600,600,480,960,600,120,600,120,960,1080,840,0,240,840,1200,360,960,600,480,480,360,960,360,240,480,720,1200,960,120,480,840,840,240,480,480,720,480],
        'o' : [0.6111111,4.6666665,1.3333334,3.2777777,3.3888888,1.3333334,3.2222223,3.5,1.4444444,4.1666665,3.3888888,1.9444444,3.3333333,4.111111,2.7777777,1.2777778,3.3333333,2.6111112,3.9444444,1.1666666,5.7222223,3.9444444,5.5555553,3.2777777,3.2222223,2.6666667,5.7222223,3.3888888,0.6666667,3.5,0.7777778,5.4444447,6.111111,4.611111,0,1.3333334,4.7222223,6.611111,1.4444444,9.388889,3.1666667,2.8888888,2.9444444,2.0555556,5.388889,2.1666667,1.4444444,3,3.7777777,6.888889,6.9444447,0.6111111,2.6111112,4.5,4.7222223,1.2777778,2.4444444,2.7777777,4.2222223,2.6666667],
        'u' : [75.49586154,69.20454565,69.20454337,70.37750022,68.07004408,69.20454337,71.5909038,52.72726853,63.88111639,77.50908679,27.22801763,71.18181064,41.52272602,67.33414758,83.04545396,72.21344127,69.20454337,70.67697647,35.08962768,79.09091062,72.56398178,70.17925536,58.13181777,70.37750022,71.5909038,69.20454138,64.50131714,68.07004408,69.20454337,65.90908567,59.31818785,67.79220559,67.94627966,70.03834015,-1,69.20454337,68.39036995,69.78608935,95.82167459,39.31145334,72.84689174,63.88111724,62.67581055,67.33414758,68.49109341,63.88111866,63.88111639,61.51514887,73.27540234,66.97214149,53.14908612,75.49586154,70.67697647,71.76767982,68.39036995,72.21344127,75.49586035,66.43636317,65.56219858,69.20454138],
        'v' : [1,7,2,5,5,2,5,4,2,7,2,3,3,6,5,2,5,4,3,2,9,6,7,5,5,4,8,5,1,5,1,8,9,7,0,2,7,10,3,8,5,4,4,3,8,3,2,4,6,10,8,1,4,7,7,2,4,4,6,4],
    },

    {
        'name' : '475',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 300,
        'k' : [7.00821,7.2538595,9.797045,10.519541,8.771101,8.525452],
        'q' : [480,420,660,660,588,564],
        'o' : [2.6944444,2.7888887,3.766667,4.044444,3.3722222,3.277778],
        'u' : [68.4910983,57.9002116,67.36725206,62.74038002,67.03833418,66.15485021],
        'v' : [40,35,55,55,49,47],
    },

    {
        'name' : '123',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 30,
        'k' : [8.933333,6.133333,13.066668,0,4.133333,14.933332,0,5.2,17.866667,5.866667,0,9.066667,8.533334,8.4,6.4,8.4,8,5.733333,5.866667,5.733333,0,6.4,2.9333334,9.866666,7.6,11.2,8.666666,9.6,15.333332,11.866668,0,15.466667,5.6,0,5.2,15.733333,2.666667,9.466666,0,2.9333334,2.5333335,8.666666,2.9333334,3.2,9.866666,5.866667,5.466666,0,8.666666,2.9333334,14.266667,2.8,12.133332,11.6,6.666666,18.933332,6.266667,16.933332,12.4,5.333334],
        'q' : [360,240,480,0,120,600,0,240,720,240,0,360,360,360,240,360,120,240,240,240,0,240,120,360,360,480,360,360,480,480,0,600,240,0,240,600,120,360,0,120,120,360,120,120,360,240,240,0,360,120,600,120,480,480,240,720,240,360,480,240],
        'o' : [3.7222223,2.5555556,5.4444447,0,1.7222222,6.2222223,0,2.1666667,7.4444447,2.4444444,0,3.7777777,3.5555556,3.5,2.6666667,3.5,3.3333333,2.3888888,2.4444444,2.3888888,0,2.6666667,1.2222222,4.111111,3.1666667,4.6666665,3.6111112,4,6.388889,4.9444447,0,6.4444447,2.3333333,0,2.1666667,6.5555553,1.1111112,3.9444444,0,1.2222222,1.0555556,3.6111112,1.2222222,1.3333334,4.111111,2.4444444,2.2777777,0,3.6111112,1.2222222,5.9444447,1.1666666,5.0555553,4.8333335,2.7777777,7.888889,2.6111112,7.0555553,5.1666665,2.2222223],
        'u' : [40.29850897,39.13043691,36.73469013,-1,29.03226041,40.17857502,-1,46.15384615,40.29850671,40.90908858,-1,39.70588089,42.1874967,42.85714286,37.5,42.85714286,15,41.86046755,40.90908858,41.86046755,-1,37.5,40.90908998,36.48648895,47.36842105,42.85714286,41.53846473,37.5,31.30435055,40.44943366,-1,38.79310261,42.85714286,-1,46.15384615,38.13559403,44.99999438,38.02817169,-1,40.90908998,47.36841794,41.53846473,40.90908998,37.5,36.48648895,40.90908858,43.90244438,-1,41.53846473,40.90908998,42.05607378,42.85714286,39.56044391,41.37931034,36.0000036,38.02817169,38.2978703,21.25984419,38.70967742,44.99999438],
        'v' : [3,2,4,0,1,5,0,2,6,2,0,3,3,3,2,3,1,2,2,2,0,2,1,3,3,4,3,3,4,4,0,5,2,0,2,5,1,3,0,1,1,3,1,1,3,2,2,0,3,1,5,1,4,4,2,6,2,3,4,2],
    },

    {
        'name' : '123',
        'start_time' : datetime(2015, 9, 1, 7, 0, 0),
        'end_time' : datetime(2015, 9, 1, 7, 30, 0),
        'interval' : 300,
        'k' : [7.6133337,6.613333,8.346666,5.706667,5.0133333,10.733335],
        'q' : [300,252,324,228,204,396],
        'o' : [3.1722224,2.7555556,3.477778,2.3777776,2.088889,4.4722223],
        'u' : [39.40455152,38.10484063,38.81789447,39.95326869,40.69148963,36.89440421],
        'v' : [25,21,27,19,17,33],
    },
]