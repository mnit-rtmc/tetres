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
package user.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.route.Route;
import user.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ReliabilityRouteInfo  extends InfoBase {
    public String name;
    public String description;
    public String corridor;
    public Route route;

    public ReliabilityRouteInfo() {        
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_TTROUTE);
    }

    public ReliabilityRouteInfo(Route r) {
        this.name = r.name;
        this.description = r.desc;
        this.corridor = r.getRNodes().get(0).corridor;
        this.route = r;
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_TTROUTE);
    }

    @Override
    public String toString() {
        return this.name;
    }

    @Override
    public ReliabilityRouteInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, ReliabilityRouteInfo.class);
    }
}
