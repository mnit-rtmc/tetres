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
import user.TeTRESConfig;

import java.util.List;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class EstimationRequestInfo  extends InfoBase {
    public ReliabilityRouteInfo travel_time_route;
    public String start_date;
    public String end_date;
    public String start_time;
    public String end_time;
    public WeekdayConditionInfo weekdays;
    public Boolean except_holiday;
    public ReliabilityEstimationModeInfo estmation_mode;
    public List<OperatingConditionsInfo> operating_conditions;
    public OperatingConditionParameterInfo oc_param;
    public Boolean write_spreadsheets = true;
    public Boolean write_graph_images = true;

    // faverolles 10/8/2019:
    public Boolean write_moe_spreadsheet = false;


    public EstimationRequestInfo() {        
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_EST_REQUEST);
    }
    
    public static EstimationRequestInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, EstimationRequestInfo.class);
    }

    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }
    
    @Override
    public EstimationRequestInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, EstimationRequestInfo.class);
    }    
}
