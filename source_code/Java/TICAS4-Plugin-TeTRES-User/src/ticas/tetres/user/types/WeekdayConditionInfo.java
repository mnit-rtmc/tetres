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
import ticas.tetres.user.TeTRESConfig;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class WeekdayConditionInfo extends InfoBase {
        public Boolean sunday;
        public Boolean monday;
        public Boolean tuesday;
        public Boolean wednesday;
        public Boolean thursday;
        public Boolean friday;
        public Boolean saturday;
        
    public WeekdayConditionInfo() {        
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_WEEKDAYS);
    }
    
    @Override
    public WeekdayConditionInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, WeekdayConditionInfo.class);
    }            

    public boolean isNotSet() {
        if(!this.sunday && !this.monday && !this.tuesday && !this.wednesday && !this.thursday && !this.friday && !this.saturday) {
            return true;
        }
        return false;
    }
}
