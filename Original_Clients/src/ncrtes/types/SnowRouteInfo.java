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
package ncrtes.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.route.Route;
import ncrtes.NCRTESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowRouteInfo extends InfoBase {

    public String name;
    public String description;
    public Integer snowroute_group_id;    
    public Route route1;
    public Route route2;
    public SnowRouteGroupInfo _snowroute_group;

    public SnowRouteInfo() {
        this.setTypeInfo(NCRTESConfig.INFO_TYPE_SNOWROUTE);
    }

    public SnowRouteInfo(Route r1, Route r2) {
        this.setTypeInfo(NCRTESConfig.INFO_TYPE_SNOWROUTE);
        this.name = r1.name;
        this.description = r1.desc;
        this.route1 = r1;
        this.route2 = r2;
    }

    @Override
    public String toString() {
        return this.name;
    }
    
    @Override
    public SnowRouteInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, SnowRouteInfo.class);
    }
   
}
