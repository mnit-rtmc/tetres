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
package ticas.common.infra;

import ticas.common.pyticas.ApiURIs;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import ticas.common.config.Config;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Infra {

    private static Infra _instance = new Infra();

    private InfraInfo infraList;
    private boolean isReady = false;
    private boolean loadFail = false;

    public final String ROUTE = "route";
    public final String CACHE = "cache";
    public final String LOG = "log";
    public final String DB = "db";

    private Infra() {
    }

    public static Infra getInstance() {
        return _instance;
    }

    public void setInfraInfo(InfraInfo infraList) {
        this.infraList = infraList;
        ApiURIs.URI = this.infraList.api_urls;
        
        for(Corridor corr : this.getCorridors()) {
            int n_stations = corr.stations.size();
            for(int idx=0; idx<n_stations; idx++) {
                this.getRNode(corr.stations.get(idx)).order =  idx;
            }
        }    
        
        if(Config.USE_LOCAL_PYTHON_SERVER) {
            String dataPath = this.getDataPath();
            Config.setDataPath(dataPath);
        }
        
        this.isReady = true;
    }
    
    public InfraInfo getInfraList() {
        return this.infraList;
    }

    public InfraConfig getConfig() {
        if(this.infraList != null) {
            return this.infraList.config;
        } else {
            return null;
        }
    }

    public List<Corridor> getCorridors() {
        return this.infraList.corridor_list;
    }

    public Corridor getCorridor(String corridor_name) {
        for (Corridor corr : this.infraList.corridor_list) {
            if (corridor_name.equals(corr.name)) {
                return corr;
            }
        }
        return null;
    }

    public Corridor getCorridor(String route, String direction) {
        for (Corridor corr : this.infraList.corridor_list) {
            if (route.equals(corr.route) && direction.equals(corr.dir)) {
                return corr;
            }
        }
        return null;
    }

    public RNode getRNode(String rnode_name) {
        if (rnode_name.startsWith("S")) {
            return this.getRNodeByStationId(rnode_name);
        }
        return this.infraList.rnode_list.get(rnode_name);
    }
    
    public List<RNode> getRNodes(List<String> rnode_names) {
        List<RNode> rnodes = new ArrayList<RNode>();
        for(String rn : rnode_names) {
            rnodes.add(this.getRNode(rn));
        }
        return rnodes;
    }

    public RNode getRNodeByStationId(String station_id) {
        for (RNode rn : this.infraList.rnode_list.values()) {
            if (station_id.equals(rn.station_id)) {
                return rn;
            }
        }
        return null;
    }

    public Detector getDetector(String detector_name) {
        return this.infraList.detector_list.get(detector_name);
    }

    public DMS getDMS(String dms_name) {
        return this.infraList.dms_list.get(dms_name);
    }

    public Camera getCamera(String cam_name) {
        return this.infraList.camera_list.get(cam_name);
    }

    public Meter getMeter(String meter_name) {
        return this.infraList.meter_list.get(meter_name);
    }

    public boolean isRNode(InfraObject obj) {
        return obj instanceof RNode;
    }

    public boolean isRNode(String obj_name) {
        return getRNode(obj_name) != null;
    }

    public boolean isDetector(InfraObject obj) {
        return obj instanceof Detector;
    }

    public boolean isDetector(String obj_name) {
        return getDetector(obj_name) != null;
    }

    public boolean isMeter(InfraObject obj) {
        return obj instanceof Meter;
    }

    public boolean isMeter(String obj_name) {
        return getMeter(obj_name) != null;
    }

    public boolean isDMS(InfraObject obj) {
        return obj instanceof DMS;
    }

    public boolean isDMS(String obj_name) {
        return getDMS(obj_name) != null;
    }

    public boolean isCamera(InfraObject obj) {
        return obj instanceof Camera;
    }

    public boolean isCamera(String obj_name) {
        return getCamera(obj_name) != null;
    }

    public boolean isStation(InfraObject obj) {
        if (this.isRNode(obj)) {
            RNode rn = (RNode) obj;
            return !rn.station_id.isEmpty();
        }
        return false;
    }

    public boolean isStation(String obj_name) {
        RNode rn = getRNode(obj_name);
        if (rn == null) {
            return false;
        }
        return !rn.station_id.isEmpty();
    }

    public boolean isAvailableStation(InfraObject obj) {
        if (!isStation(obj)) {
            return false;
        }
        RNode rn = (RNode) obj;
        if (rn.detectors.isEmpty()) {
            return false;
        }
        return true;
    }

    public boolean isAvailableStation(String obj_name) {
        return isAvailableStation(getRNode(obj_name));
    }

    public boolean isEntrance(InfraObject obj) {
        if (this.isRNode(obj)) {
            RNode rn = (RNode) obj;
            return rn.n_type.equals("Entrance");
        }
        return false;
    }

    public boolean isEntrance(String obj_name) {
        return isEntrance(getRNode(obj_name));
    }

    public boolean isExit(InfraObject obj) {
        if (this.isRNode(obj)) {
            RNode rn = (RNode) obj;
            return rn.n_type.equals("Exit");
        }
        return false;
    }
    
    public boolean isExit(String obj_name) {
        return isExit(getRNode(obj_name));
    }    

    public boolean isCDExit(InfraObject obj) {
        if (this.isRNode(obj)) {
            RNode rn = (RNode) obj;
            return rn.n_type.equals("Exit") && rn.transition.equals("CD");
        }
        return false;
    }
    
    public boolean isCDExit(String obj_name) {
        return isCDExit(getRNode(obj_name));
    }      

    public boolean isCDEntrance(InfraObject obj) {
        if (this.isRNode(obj)) {
            RNode rn = (RNode) obj;
            return rn.n_type.equals("Entrance") && rn.transition.equals("CD");
        }
        return false;
    }
    
    public boolean isCDEntrance(String obj_name) {
        return isCDEntrance(getRNode(obj_name));
    }      

    public double getDistanceInMile(String rnode1, String rnode2) {
        RNode rn1 = getRNode(rnode1);
        RNode rn2 = getRNode(rnode1);
        return getDistanceInMile(rn1, rn2);
    }
    
    public double getDistanceInMile(RNode rnode1, RNode rnode2) {
        return this.getDistanceInMile(rnode1.lat, rnode1.lon, rnode2.lat, rnode2.lon);
    }    

    public double getDistanceInFeet(String rnode1, String rnode2) {
        return this.getDistanceInMile(rnode1, rnode2) * this.getConfig().FEET_PER_MILE;
    }
    
    public double getDistanceInFeet(RNode rnode1, RNode rnode2) {
        return this.getDistanceInMile(rnode1, rnode2) * this.getConfig().FEET_PER_MILE;
    }    

    public double getDistanceInMile(float lat1, float lon1, float lat2, float lon2) {
        double rad_lon1 = deg2rad(lon1);
        double rad_lon2 = deg2rad(lon2);
        double rad_lat1 = deg2rad(lat1);
        double rad_lat2 = deg2rad(lat2);
        double dlat = rad_lat2 - rad_lat1;
        double dlon = rad_lon2 - rad_lon1;
        double a = Math.pow(Math.sin(dlat / 2), 2) + Math.cos(rad_lat1) * Math.cos(rad_lat2) * Math.pow(Math.sin(dlon / 2), 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return c * this.getConfig().RADIUS_IN_EARTH_FOR_MILE;
    }

    private double deg2rad(double deg) {
        return deg * Math.PI / 180.0;
    }

    public String getPath(String subDirName) {
        return getDataPath() + File.separator + subDirName;
    }
    
    public String getDataPath() {
        File dataDir = new File(Config.getDataPath());
        if(!dataDir.exists()) {
            dataDir.mkdir();
        } 
        return dataDir.getAbsolutePath();
    }

    public boolean isInfraReady() {
        return this.isReady;
    }

    public void setFailToLoadInfra(boolean b) {
        this.loadFail = b;
    }
    
    public boolean isFailToLoadInfra() {
        return this.loadFail;
    }
    
}
