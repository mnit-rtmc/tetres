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
package admin.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.log.TICASLogger;
import admin.TeTRESConfig;
import admin.types.ActionType;
import admin.types.InfoBase;

import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ActionLogInfo extends InfoBase {

    public String action_type;
    public String target_datatype;
    public String target_table;
    public String target_id;
    public String data_desc;
    public Boolean handled;
    public String handled_date;
    public String status;
    public String status_updated_date;
    public String reason;
    public String user_ip;
    public String reg_date;

    public ActionLogInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_ACTIONLOG);
    }

    @Override
    public ActionLogInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, ActionLogInfo.class);
    }

    public Object getStatus() {

        if (ActionType.STATUS_RUNNING.equals(this.status)) {
            return "running..";
        }
        
        if (ActionType.STATUS_FAIL.equals(this.status)) {
            return String.format("process failed at %s (%s)", this.status_updated_date, this.reason);
        }        
        
        if (this.handled) {
            if (ActionType.DELETE.equals(this.action_type)) {
                return String.format("deleted at %s", this.handled_date);
            }
            if (ActionType.UPDATE.equals(this.action_type)) {
                return String.format("updated and processed at %s", this.handled_date);
            }
            if (ActionType.INSERT.equals(this.action_type)) {
                return String.format("added and processed at %s", this.handled_date);
            }            
        }
        
        return String.format("in queue");        
    }
}
