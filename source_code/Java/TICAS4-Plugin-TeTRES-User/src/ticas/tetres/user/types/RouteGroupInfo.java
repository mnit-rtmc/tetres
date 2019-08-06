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
package ticas.tetres.user.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.infra.RNode;
import ticas.common.route.Route;
import java.util.ArrayList;
import java.util.List;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class RouteGroupInfo {

    public String name;
    public List<ReliabilityRouteInfo> route_list = new ArrayList<ReliabilityRouteInfo>();

    public RouteGroupInfo() {
    }

    public RouteGroupInfo(String name) {
        this.name = name;
    }

    public static RouteGroupInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, RouteGroupInfo.class);
    }

    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }

    @Override
    public RouteGroupInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, RouteGroupInfo.class);
    }

    @Override
    public String toString() {
        return this.name;
    }

    public List<Route> getRouteList() {
        List<Route> routeList = new ArrayList<Route>();
        for (ReliabilityRouteInfo rri : this.route_list) {
            routeList.add(rri.route);
        }
        return routeList;
    }

    public GeoPosition getCenter() {
        float totalLat = 0.0f;
        float totalLon = 0.0f;
        int cnt = 0;
        for (ReliabilityRouteInfo rri : this.route_list) {
            for (RNode rn : rri.route.getRNodes()) {
                totalLat += rn.lat;
                totalLon += rn.lon;
                cnt ++;
            }
        }
        if(cnt == 0) {
            return null;
        }
        return new GeoPosition(totalLat/cnt, totalLon/cnt);
    }
}
