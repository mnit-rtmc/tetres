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

package common.infra;

import java.util.List;
import java.util.Map;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Corridor {
    public List<String> accesses;
    public List<String> cameras;
    public List<String> dmss;
    public List<String> entrances;
    public List<String> exits;
    public List<String> interchanges;
    public List<String> intersections;
    public List<String> rnodes;
    public List<String> stations;
    public Map<String, String> rnode_station;
    public Map<String, String> station_rnode;
    public String dir;
    public String name;
    public String route;
    
    @Override
    public String toString() {
        return this.name;
    }    
}
