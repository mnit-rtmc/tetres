# -*- coding: utf-8 -*-
__author__ = 'Chongmyung Park (chongmyung.park@gmail.com)'

from sqlalchemy.dialects import postgresql

def query_string(qry):
    return str(qry.statement.compile(dialect=postgresql.dialect()))
