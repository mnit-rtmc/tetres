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
package admin.api;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ApiURIs {

    public static ApiURIs URI;

    // ttroute configurations
    public String TTROUTE_LIST;
    public String TTROUTE_DELETE;
    public String TTROUTE_INSERT;
    public String TTROUTE_GET;
    public String TTROUTE_UPDATE;
    public String TTROUTE_OPPOSITE_ROUTE;

    // wz configurations
    public String WZ_LIST;
//    public String WZ_LIST_BY_YEAR;
    public String WZ_DELETE;
    public String WZ_INSERT;
    public String WZ_GET;
    public String WZ_UPDATE;
//    public String WZ_YEARS;
    
    // wz configurations
    public String WZ_GROUP_LIST;
    public String WZ_GROUP_LIST_BY_YEAR;
    public String WZ_GROUP_DELETE;
    public String WZ_GROUP_INSERT;
    public String WZ_GROUP_GET;
    public String WZ_GROUP_UPDATE;
    public String WZ_GROUP_YEARS;    

    // special event
    public String SE_LIST;
    public String SE_LIST_BY_YEAR;
    public String SE_DELETE;
    public String SE_UPDATE;
    public String SE_INSERT;
    public String SE_GET;
    public String SE_YEARS;
    // faverolles 1/15/2020: Adding For Use By Bulk Insert From CSV
    public String SE_INSERT_ALL;

    // snow management
    public String SNM_LIST;
    public String SNM_DELETE;
    public String SNM_UPDATE;
    public String SNM_INSERT;
    public String SNM_INSERT_ALL;
    public String SNM_GET;
    public String SNM_YEARS;
    
    // snow route
    public String SNR_LIST;
    public String SNR_DELETE;
    public String SNR_UPDATE;
    public String SNR_INSERT;
    public String SNR_GET;
    public String SNR_YEARS;
    
    // snow event
    public String SNE_LIST;
    public String SNE_LIST_BY_YEAR;
    public String SNE_DELETE;
    public String SNE_UPDATE;
    public String SNE_INSERT;
    public String SNE_GET;
    public String SNE_YEARS;
    
    // action log
    public String AL_LIST;
    public String AL_PROCEED;
    
    // route
    public String ROUTE_FROM_CFG;
    public String ROUTE_XLSX;
    
    // system config
    public String SYSCFG_GET;
    public String SYSCFG_UPDATE;


    public String RW_MOE_PARAM_LIST;
    public String RW_MOE_PARAM_INSERT;

}
