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
package ticas.tetres.admin.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.tetres.admin.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class WorkZoneGroupInfo extends InfoBase {
    
    public String name;
    public String description;
    public String years;
    public String corridors;

    public WorkZoneGroupInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_WORKZONE_GROUP);
    }
    
    public String getYears() {
        if(this.years.isEmpty()) return "";
        String[] ys = this.years.split(",");
        if(ys.length == 1) return this.years;
        return String.format("%s-%s", ys[0], ys[ys.length-1]);
    }
    
    @Override
    public String toString() {
        return this.name;
    }

    @Override
    public WorkZoneGroupInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, WorkZoneGroupInfo.class);
    }
}
