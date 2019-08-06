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
package ticas.common.config;

import static ticas.common.config.FilePreferencesFactory.SYSTEM_PROPERTY_FILE;
import ticas.common.config.ui.ConfigDialog;
import ticas.common.config.ui.ConfigType;
import ticas.common.log.TICASLogger;
import ticas.common.ui.map.MapProvider;
import ticas.common.ui.map.TileServerFactory;
import ticas.common.util.FileHelper;

import java.awt.Component;
import java.awt.Frame;
import java.io.*;
import java.nio.channels.Channels;
import java.nio.channels.ReadableByteChannel;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.prefs.Preferences;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.Level;
import org.apache.http.*;
import org.apache.http.client.*;
import org.apache.http.client.methods.*;
import org.apache.http.impl.client.*;
import ticas.common.ui.map.BaseOSMProvider;
import org.rauschig.jarchivelib.*;
import java.util.zip.*;
import java.util.stream.*;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Config {

    public static final String PREFERENCE_FILE = "ticas.prefs";
    public static Boolean USE_LOCAL_PYTHON_SERVER = true;
    private static final String DEFAULT_LOG_LEVEL = "INFO";
    private static final String DEFAULT_PYTHON_EXE_PATH = "python.exe";
    private static final String DEFAULT_PYTHON_SERER_PATH = FileHelper.currentPath() + File.separator + "server.py";
    private static final String DEFAULT_PYTHON_SERVER_URL = "http://localhost";
    private static final String DEFAULT_PYTHON_SERVER_PORT = "5000";
    private static final String DEFAULT_DATA_PATH = FileHelper.currentPath() + File.separator + "data";
    private static final Boolean DEFAULT_TERMINATE_SERVER_ON_EXIT = false;

    private static boolean initalized = false;
    private static Preferences prefs;
    private static List<AbstractConfigChangeListener> changeListeners = new ArrayList<>();
    public static Frame mainFrame;
	public static String zipURL;
	public static String pythonServerURL = null;

	/** <FileName, Contents> of zip file from server */
	private static Map<String, String> initialFiles = new HashMap<>();

    public static void addConfigChangeListener(AbstractConfigChangeListener listener) {
        changeListeners.add(listener);
    }

    public static void removeConfigChangeListener(AbstractConfigChangeListener listener) {
        changeListeners.remove(listener);
    }

    public static void init(Component frame) {

        if (initalized) {
            return;
        }

        initalized = true;
		
        System.setProperty("java.util.prefs.PreferencesFactory", FilePreferencesFactory.class.getName());
        System.setProperty(SYSTEM_PROPERTY_FILE, PREFERENCE_FILE);
        prefs = Preferences.userRoot().node("ticas");

//        if (new File(PREFERENCE_FILE).exists() && prefs.get("python_exe_path", null) != null) {
//            return;
//        }
        
        while(!checkConfigs()) {
            showDialog(frame);
        }
    }

	/**
	 * Downloads data.zip from server and puts each entry in initialFiles
	 */
	private static boolean downloadDataDirectory() {
		try {
			URL url = new URL(zipURL);
			HttpClient httpClient = HttpClientBuilder.create().build();
			HttpGet httpGet = new HttpGet(zipURL);
			HttpResponse response = httpClient.execute(httpGet);

			InputStream in = response.getEntity().getContent();
			ZipInputStream zis = new ZipInputStream(in);
			ZipEntry ze;
			int lengthRead;
			byte[] buf = new byte[1024];
			while ((ze = zis.getNextEntry()) != null) {
				StringBuilder sb = new StringBuilder();
				while ((lengthRead = zis.read(buf, 0, 1024)) >= 0)
					sb.append(new String(buf, 0, lengthRead));
				initialFiles.put(ze.getName(), sb.toString());
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		return true;
	}

	/** 
	 * Filter (path, contents) down to route groups, then collect the file
	 * contents in a list. Called by RouteGroupInfoHelper.
	 */
	public static List<String> getDownloadedRouteGroups() {
		return initialFiles.entrySet().stream()
				.filter(e -> e.getKey().contains("tetres/route-groups"))
				.sorted(Map.Entry.comparingByKey())
				.map(e -> e.getValue())
				.collect(Collectors.toList());
	}

	/** 
	 * Filter (path, contents) down to just filters, then collect the file
	 * contents in a list. Called by OperatingConditionInfoHelper.
	 */
	public static List<String> getDownloadedOCs() {
		return initialFiles.entrySet().stream()
				.filter(e -> e.getKey().contains("tetres/filters"))
				.sorted(Map.Entry.comparingByKey())
				.map(e -> e.getValue())
				.collect(Collectors.toList());
	}

	/** 
	 * Get the downloaded requested.json, then return the file
	 * contents. Called by UIHelper.
	 */
	public static String getDownloadedRequestInfo() {
		return initialFiles.get("server/data/tetres/requested.json");
	}

    private static boolean checkConfigs() {
		// Download data directory every time the application is run
		boolean downloaded = downloadDataDirectory();
		if (!downloaded) {
			JOptionPane.showMessageDialog(mainFrame, "Download from server failed.");
			return false;
		}

        // check custom map provider
        String providerName = prefs.get("map_provider", MapProvider.TMC.name());
        if (providerName.equals(MapProvider.CUSTOM.name())) {
            BaseOSMProvider customProvider = MapProvider.CUSTOM.getProvider();
            String osmServerURL = getCustomOSMServerURL();
            if (osmServerURL.isEmpty() || !osmServerURL.startsWith("http")) {
                JOptionPane.showMessageDialog(mainFrame, "Enter Custom OSM Server URL (init)");
                return false;
            }
            customProvider.clearBaseURLs();
            customProvider.addBaseURLs(osmServerURL);
        }

        // check if map server is available
        MapProvider mapProvider = getMapProvider();
        BaseOSMProvider osmProvider = mapProvider.getProvider();
        if (!osmProvider.isAvailable()) {
            if (JOptionPane.showConfirmDialog(mainFrame, "The selected map server is not available.\nDo you want to change the map server?", "Confirm", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
                return false;
            }
        }

        return true;
    }

    public static void showDialog(Component frame) {
        List<Object> logLevelChoices = new ArrayList<>();
        logLevelChoices.add("TRACE");
        logLevelChoices.add("DEBUG");
        logLevelChoices.add("INFO");
        logLevelChoices.add("WARN");
        logLevelChoices.add("ERROR");
        logLevelChoices.add("FATAL");

        List<Object> mapProviderChoices = new ArrayList<>();
        for (MapProvider mp : MapProvider.values()) {
            mapProviderChoices.add(mp.name());
        }

        ConfigDialog cd = new ConfigDialog(null, true);
        if (USE_LOCAL_PYTHON_SERVER) {
            cd.addConfig("python_exe_path", "Python Interpreter Path", getPythonPath(), ConfigType.FILE);
            cd.addConfig("python_server_path", "PyTICAS Server Script Path", getServerPath(), ConfigType.FILE);
        }
        cd.addConfig("python_server_url", "PyTICAS Server URL", getServerURL(), ConfigType.STRING);
        cd.addConfig("python_server_port", "PyTICAS Server Port", getServerPort(), ConfigType.INTEGER);
        if (USE_LOCAL_PYTHON_SERVER) {
            cd.addConfig("python_terminate_server_on_exit", "Terminate PyTICAS Server when exiting TICAS", getTerminateServerOnExit(), ConfigType.BOOLEAN);
        } else {
            cd.addConfig("data_path", "Data directory path", getDataPath(), ConfigType.DIRECTORY);
        }
        cd.addConfig("log_level", "Log Level", getLogLevel(), logLevelChoices, ConfigType.STRING);
        cd.addConfig("map_provider", "Map Provider", getMapProvider().name(), mapProviderChoices, ConfigType.STRING);
        cd.addConfig("custom_osm_server", "Custom OSM Server URL", getCustomOSMServerURL(), ConfigType.STRING);
        cd.setLocationRelativeTo(frame);
        cd.setVisible(true);

        if (cd.shouldUpdate()) {
            if (USE_LOCAL_PYTHON_SERVER) {
                setPythonPath(cd.getStringValue("python_exe_path"));
                setServerPath(cd.getStringValue("python_server_path"));
            }
            setServerURL(cd.getStringValue("python_server_url"));
            setServerPort(cd.getStringValue("python_server_port"));
            if (USE_LOCAL_PYTHON_SERVER) {
                setTerminateServerOnExit(cd.getBooleanValue("python_terminate_server_on_exit"));
            } else {
                setDataPath(cd.getStringValue("data_path"));
            }
            setLogLevel(cd.getStringValue("log_level"));
            setCustomOSMServerURL(cd.getStringValue("custom_osm_server"));
            setMapProvider(MapProvider.valueOf(cd.getStringValue("map_provider")));
        }
    }

    public static String getPythonPath() {
        return prefs.get("python_exe_path", DEFAULT_PYTHON_EXE_PATH);
    }

    public static void setPythonPath(String pythonPath) {
        prefs.put("python_exe_path", pythonPath);
    }

    public static String getServerPath() {
        return prefs.get("python_server_path", DEFAULT_PYTHON_SERER_PATH);
    }

    public static void setServerPath(String pythonPath) {
        prefs.put("python_server_path", pythonPath);
    }

    public static String getServerPort() {
        return prefs.get("python_server_port", DEFAULT_PYTHON_SERVER_PORT);
    }

    public static void setServerPort(String serverPort) {
        prefs.put("python_server_port", serverPort);
    }

    public static String getServerURL() {
		if (pythonServerURL != null && !pythonServerURL.equals(""))
			return prefs.get("python_server_url", pythonServerURL);
        return prefs.get("python_server_url", DEFAULT_PYTHON_SERVER_URL);
    }

    public static void setServerURL(String serverURL) {
        prefs.put("python_server_url", serverURL);
    }

    static public String getAPIUrl(String uri_path) {
        return String.format("%s:%s%s", getServerURL(), getServerPort(), uri_path);
    }

    public static void setTerminateServerOnExit(Boolean v) {
        prefs.putBoolean("python_terminate_server_on_exit", v);
    }

    static public Boolean getTerminateServerOnExit() {
        return prefs.getBoolean("python_terminate_server_on_exit", DEFAULT_TERMINATE_SERVER_ON_EXIT);
    }

    public static String getDataPath() {
        return prefs.get("data_path", DEFAULT_DATA_PATH);
    }

    public static void setDataPath(String dataPath) {
        File dp = new File(dataPath);
        if (!dp.exists()) {
            JOptionPane.showMessageDialog(mainFrame, "Data directory does not exists!");
            showDialog(mainFrame);
            return;
        }        
        prefs.put("data_path", dataPath);
    }

    public static void setLogLevel(String logLevel) {
        prefs.put("log_level", logLevel);
        TICASLogger.setLogLevel(Level.getLevel(logLevel));
    }

    static public String getLogLevel() {
        return prefs.get("log_level", DEFAULT_LOG_LEVEL);
    }

    public static void setMapProvider(MapProvider provider) {

        prefs.put("map_provider", provider.name());

        // check custom map provider
        if (provider.name().equals(MapProvider.CUSTOM.name())) {
            BaseOSMProvider customProvider = MapProvider.CUSTOM.getProvider();
            String osmServerURL = getCustomOSMServerURL();
            if (osmServerURL.isEmpty() || !osmServerURL.startsWith("http")) {
                JOptionPane.showMessageDialog(mainFrame, "Enter Custom OSM Server URL (set)");
                showDialog(Config.mainFrame);
                return;
            }
            customProvider.clearBaseURLs();
            customProvider.addBaseURLs(osmServerURL);
        }

        BaseOSMProvider osm = provider.getProvider();
        if(!osm.isAvailable()) {
            if (JOptionPane.showConfirmDialog(mainFrame, "The selected map server is not available.\nDo you want to change the map server?", "Confirm", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
                showDialog(Config.mainFrame);
                return;
            }
        }
        
        TileServerFactory.defaultProvider = provider;
        for (AbstractConfigChangeListener listener : changeListeners) {
            listener.MapProviderChanged(provider);
        }
    }

    static public MapProvider getMapProvider() {
        String providerName = MapProvider.TMC.name();
        if (prefs != null) {
            providerName = prefs.get("map_provider", MapProvider.TMC.name());
        }
        return MapProvider.valueOf(providerName);
    }

    public static void setCustomOSMServerURL(String serverURL) {
        prefs.put("custom_osm_server", serverURL);
    }

    static public String getCustomOSMServerURL() {
        return prefs.get("custom_osm_server", "");
    }
}
