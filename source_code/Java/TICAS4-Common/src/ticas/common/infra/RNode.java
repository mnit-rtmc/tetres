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

import java.util.List;
import java.util.Map;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RNode extends InfraObject {
    public Integer order;
    public String corridor;
    public List<String> up_camera;
    public String up_entrance;
    public String up_exit;
    public String up_rnode;
    public String up_station;
    public List<String> down_camera;
    public String down_entrance;
    public String down_exit;
    public String down_rnode;
    public String down_station;      
    public String transition;        
    public String station_id;        
    public String n_type;        
    public String label;      
    public List<String> detectors;
    public List<String> meters;
    public List<String> down_dmss;
    public List<String> up_dmss;
    public List<String> forks;
    public Map<String, String> connected_to;
    public Map<String, String> connected_from;
    public Float lat;
    public Float lon;
    public Integer lanes;
    public Integer s_limit;
    public Integer shift;
    public Boolean active;    
    
    @Override
    public String toString() {
        if(this.station_id != null && !this.station_id.equals("")) {
            return this.station_id + " (" + this.name + ")";
        } else if("Entrance".equals(this.n_type)) {
            return this.label + " (E, " + this.name + ")";
        } else if("Exit".equals(this.n_type)) {
            return this.label + " (X, " + this.name + ")";
        } else {
            return this.name;
        }
        
    }
}

