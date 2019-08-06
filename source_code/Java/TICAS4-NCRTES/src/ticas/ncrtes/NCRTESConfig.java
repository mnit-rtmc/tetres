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
package ticas.ncrtes;

import ticas.ncrtes.types.NCRTESDataType;
import ticas.common.config.Config;
import ticas.common.config.ui.ConfigDialog;
import ticas.common.config.ui.ConfigType;
import java.awt.Component;
import java.util.HashMap;
import java.util.Map;
import java.util.prefs.Preferences;
import javax.swing.JFrame;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class NCRTESConfig {

    static public JFrame mainFrame;
    
    static public String API_NCRTES_INFO = "/ncrtes/info";
    static public Map<String, NCRTESDataType> dataTypes = new HashMap<String, NCRTESDataType>();

    static public String INFO_TYPE_SNOWROUTE_GROUP = "snow route group";
    static public String INFO_TYPE_SNOWROUTE = "snow route";
    static public String INFO_TYPE_SNOWEVENT = "snow event";
    static public String INFO_TYPE_ESTIMATION_REQUEST = "estimation request";
    static public String INFO_TYPE_BARELANE_REGAIN_TIME_INFO = "barelane regain time";
    static public String INFO_TYPE_TARGET_STATION = "target station";
    
    static private boolean  isInitialized = false;
    static private Preferences prefs;

    static private final String DEFAULT_SERVER_URL = "http://localhost";
    static private final String DEFAULT_SERVER_PORT = "5000";
    static public String resultDir = "ncrtes/results";
    
    static public void init() {
        if(isInitialized) return;
        Config.mainFrame = mainFrame;
        Config.init(mainFrame);        
        prefs = Preferences.userRoot().node("ncrtes");
        if(prefs.get("server_url", null) == null) {
            showDialog(mainFrame);
        }
        isInitialized = true;
    }
    
    public static void showDialog(Component frame) {
        
        ConfigDialog cd = new ConfigDialog(null, true);
        
        cd.setTitle("NCRTES Configurations");
        cd.addConfig("server_url", "NCRTES Server URL", getServerURL(), ConfigType.STRING);
        cd.addConfig("server_port", "NCRTES Server Port", getServerPort(), ConfigType.STRING);
        cd.setLocationRelativeTo(frame);
        cd.setVisible(true);
        
        if(cd.shouldUpdate()) {            
            setServerURL(cd.getStringValue("server_url"));
            setServerPort(cd.getStringValue("server_port"));
        }           
    }
        
    public static String getServerPort() {
        return prefs.get("server_port", DEFAULT_SERVER_PORT);
    }

    public static void setServerPort(String serverPort) {
        prefs.put("server_port", serverPort);
    }

    public static String getServerURL() {
        return prefs.get("server_url", DEFAULT_SERVER_URL);
    }

    public static void setServerURL(String serverURL) {
        prefs.put("server_url", serverURL);
    }

    static public String getAPIUrl(String uri_path) {
        return String.format("%s:%s%s", NCRTESConfig.getServerURL(), NCRTESConfig.getServerPort(), uri_path);
    }

}
