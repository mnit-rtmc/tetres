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
package user;

import common.config.Config;
import common.infra.Infra;
import common.util.FileHelper;
import user.types.TeTRESDataType;

import javax.swing.*;
import java.io.File;
import java.util.HashMap;
import java.util.Map;
import java.util.prefs.Preferences;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TeTRESConfig {

    static public JFrame mainFrame;

    static public String API_TETRES_INFO = "/tetres/user/info";
    static public Map<String, TeTRESDataType> dataTypes = new HashMap<String, TeTRESDataType>();

    // this `info_type` must match to data types in "tetres_types" module in the python codes
    static public String INFO_TYPE_TTROUTE = "route";
    static public String INFO_TYPE_EST_REQUEST = "estimation request info";
    static public String INFO_TYPE_WEEKDAYS = "weekdays";
    static public String INFO_TYPE_EST_MODE = "reliability estimation mode";
    static public String INFO_TYPE_OPERATING_CONDITIONS = "operating conditions";
    static public String INFO_TYPE_OC_WEATHER = "weather condition";
    static public String INFO_TYPE_OC_INCIDENT = "incident condition";
    static public String INFO_TYPE_OC_WORKZONE = "workzone condition";
    static public String INFO_TYPE_OC_SPECIALEVENT = "special event condition";
    static public String INFO_TYPE_OC_SNOWMGMT = "snow management condition";
    static public String INFO_TYPE_OPERATING_CONDITION_PARAM = "operating condition param";

    static private boolean isInitialized = false;
    static private Preferences prefs;

    static private final String DEFAULT_SERVER_URL = "http://192.168.1.8";
    static private final String DEFAULT_SERVER_PORT = "5000";

    static public String RESULT_DIR_NAME = "results";

    static public void init() {
        if (isInitialized) return;
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

    public static String getDataPath(String filename) {
        String dataPath = Infra.getInstance().getDataPath();
        String outputPath = dataPath + File.separator + "tetres";
        if (!FileHelper.exists(outputPath)) {
            FileHelper.createDirs(outputPath);
        }
        if (!FileHelper.isFilenameValid(filename)) {
            return null;
        }
        if (filename != null) {
            outputPath = outputPath + File.separator + filename;
        }
        return outputPath;
    }

    public static String getDataPath(String filename, boolean createDir) {
        String filepath = getDataPath(filename);
        if (filepath != null && createDir) {
            File f = new File(filepath);
            if (!f.exists()) {
                f.mkdir();
            }
        }
        return filepath;
    }

}
