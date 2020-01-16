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
import ncrtes.NCRTESConfig;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class EstimationRequestInfo extends InfoBase {

    public String snow_start_time = "";
    public String snow_end_time = "";
    public List<String> target_corridors = new ArrayList<String>();
    public List<Integer> target_snow_routes = new ArrayList<Integer>();
    public List<BarealaneRegainTimeInfo> barelane_regain_time_infos = new ArrayList<BarealaneRegainTimeInfo>();

    public EstimationRequestInfo() {
        this.setTypeInfo(NCRTESConfig.INFO_TYPE_ESTIMATION_REQUEST);
    }

    public EstimationRequestInfo(String module, String className) {
        this.__class__ = className;
        this.__module__ = module;
    }

    @Override
    public EstimationRequestInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, EstimationRequestInfo.class);
    }

}
