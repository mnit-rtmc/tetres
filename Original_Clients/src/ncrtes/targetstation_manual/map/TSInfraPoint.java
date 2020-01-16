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
package ncrtes.targetstation_manual.map;

import common.infra.RNode;
import common.ui.map.InfraPoint;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class TSInfraPoint extends InfraPoint {
    
    public TSInfraPoint(RNode rnode) {
        super(rnode);
        this.setPosition(new GeoPosition(rnode.lat, rnode.lon));
        this.infraObject = rnode;
        if(infra.isStation(rnode)) {
            this.name = rnode.station_id + " (" + rnode.label + ")";
        } else if(infra.isEntrance(rnode)) {
            this.name = "Ent (" + rnode.label + ")";
        } else if(infra.isExit(rnode)) {
            this.name = "Ext (" + rnode.label + ")";            
        } else {
            this.name = rnode.getInfraType() + "(" + rnode.label +")";
        }
        if(infra.isStation(rnode)) setMarkerType(MarkerType.RED);
        else if(infra.isEntrance(rnode)) setMarkerType(MarkerType.GREEN);
        else if(infra.isExit(rnode)) setMarkerType(MarkerType.PURPLE);
        else setMarkerType(MarkerType.GRAY);
    }

    public TSInfraPoint(String name, double latitude, double longitude) {
        super(name, latitude, longitude);
    }

    public TSInfraPoint(String name, double latitude, double longitude, MarkerType mtype) {
        super(name, latitude, longitude, mtype);
    }    
}
