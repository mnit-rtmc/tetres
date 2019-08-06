# -*- coding: utf-8 -*-

from pyticas_ncrtes.core.est import estimation
from pyticas_ncrtes.core.est.report import report as ncrt_report

__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

# alias estimation interfaces to sub-module
estimate = estimation.estimate
prepare_data = estimation.prepare_data
report = ncrt_report.report
