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
package admin;

import common.config.Config;
import admin.types.TTRMSDataType;
import java.util.HashMap;
import java.util.Map;
import javax.swing.JFrame;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TeTRESConfig {

    static public JFrame mainFrame;
    
    static public String API_TTRMS_INFO = "/tetres/adm/info";
    static public Map<String, TTRMSDataType> dataTypes = new HashMap<String, TTRMSDataType>();

    static public String INFO_TYPE_TTROUTE = "route";
    static public String INFO_TYPE_WORKZONE = "work zone";
    static public String INFO_TYPE_WORKZONE_GROUP = "work zone group";
    static public String INFO_TYPE_ROUTE_WISE_MOE_PARAMETER = "route wise moe parameters";
    static public String INFO_TYPE_SPECIAL_EVNET = "special event";
    static public String INFO_TYPE_SNOWMGMT = "snow management";
    static public String INFO_TYPE_SNOWROUTE = "snow route";
    static public String INFO_TYPE_SNOWEVENT = "snow event";
    static public String INFO_TYPE_ACTIONLOG = "action log";
    static public String INFO_TYPE_SYSTEMCONFIG = "system config";
    
    static private boolean  isInitialized = false;

    static public void init() {
        if(isInitialized) return;       
        Config.init(mainFrame);        
        isInitialized = true;
    }
            
    public static String getServerPort() {
        return Config.getServerPort();
    }

    public static void setServerPort(String serverPort) {
        Config.setServerPort(serverPort);
    }

    public static String getServerURL() {
        return Config.getServerURL();
    }

    public static void setServerURL(String serverURL) {
        Config.setServerURL(serverURL);
    }

    static public String getAPIUrl(String uri_path) {
        return String.format("%s:%s%s", TeTRESConfig.getServerURL(), TeTRESConfig.getServerPort(), uri_path);
    }

}
