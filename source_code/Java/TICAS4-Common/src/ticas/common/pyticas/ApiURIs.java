/*
 * Copyright (C) 2018 NATSRL @ UMD (University Minnesota Duluth)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package ticas.common.pyticas;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ApiURIs {
    
    public static ApiURIs URI;
    
    public static String INFO_INFRA = "/ticas/infra";
    
    public String CHECK_CFG_DATE;   
    
    public String MOE_TT;
    public String MOE_SPEED;
    public String MOE_DENSITY;
    public String MOE_TOTAL_FLOW;
    public String MOE_AVG_FLOW;
    public String MOE_OCCUPANCY;
    public String MOE_ACCELERATION;
    public String MOE_VMT;
    public String MOE_LVMT;
    public String MOE_VHT;
    public String MOE_DVH;
    public String MOE_MRF;
    public String MOE_STT;
    public String MOE_SV;
    public String MOE_CM;
    public String MOE_CMH;
    public String MOE_RWIS;
    
    public String ROUTE_LIST;
    public String ROUTE_DELETE;
    public String ROUTE_ADD;
    public String ROUTE_GET;
    public String ROUTE_CFG_SAVE;
    public String ROUTE_UPDATE_CFG;
    
    public String ROUTE_FROM_XLSX;
    public String ROUTE_TO_XLSX;
    public String ROUTE_FROM_JSON;
}
