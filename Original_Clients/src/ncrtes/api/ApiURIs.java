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
package ncrtes.api;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ApiURIs {

    public static ApiURIs URI;
    
    public String ESTIMATION;
    
    // snow route
    public String SNR_LIST;
    public String SNR_DELETE;
    public String SNR_UPDATE;
    public String SNR_INSERT;
    public String SNR_GET;
    
    public String SNR_GROUP_YEARS;
    public String SNR_GROUP_LIST;
    public String SNR_GROUP_LIST_BY_YEAR;
    public String SNR_GROUP_DELETE;
    public String SNR_GROUP_UPDATE;
    public String SNR_GROUP_INSERT;
    public String SNR_GROUP_GET;
    public String SNR_GROUP_COPY;
        
    // snow event
    public String SNE_LIST;
    public String SNE_LIST_BY_YEAR;
    public String SNE_DELETE;
    public String SNE_UPDATE;
    public String SNE_INSERT;
    public String SNE_GET;
    public String SNE_YEARS;
    
    // target station
    public String TS_LIST;
    public String TS_DELETE;
    public String TS_UPDATE;
    public String TS_YEARS;    
    
    // manual target station (deprecated)
    public String MANUAL_TS_LIST;
    public String MANUAL_TS_DELETE;
    public String MANUAL_TS_INSERT;
    
    // target station identification
    public String TSI;
}
