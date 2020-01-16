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
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 *
 * @author Chongmyung Park (chongmyung.park@gmail.com)
 */
public class BarealaneRegainTimeInfo extends InfoBase {

    public String truckroute_id;
    public String snow_start_time;
    public String snow_end_time;
    public String lane_lost_time;
    public String barelane_regain_time;
    
    public BarealaneRegainTimeInfo(String truckRouteId, Date snowStartTime, Date snowEndTime, Date laneLostTime, Date barelaneRegainTime) {
        this.setTypeInfo(NCRTESConfig.INFO_TYPE_BARELANE_REGAIN_TIME_INFO);
        this.truckroute_id = truckRouteId;
        DateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:00");
        if(snowStartTime != null)
            this.snow_start_time = df.format(snowStartTime);
        if(snowEndTime != null)
            this.snow_end_time = df.format(snowEndTime);
        if(laneLostTime != null)
            this.lane_lost_time = df.format(laneLostTime);
        if(barelaneRegainTime != null)
            this.barelane_regain_time = df.format(barelaneRegainTime);
    }    

    @Override
    public BarealaneRegainTimeInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, BarealaneRegainTimeInfo.class);
    }
       
    
}
