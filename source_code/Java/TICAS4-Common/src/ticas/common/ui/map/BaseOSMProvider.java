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
package ticas.common.ui.map;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URI;
import java.net.URISyntaxException;
import ticas.common.log.TICASLogger;
import java.net.URL;
import java.net.URLConnection;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import org.apache.logging.log4j.core.Logger;
import org.jdesktop.swingx.mapviewer.DefaultTileFactory;
import org.jdesktop.swingx.mapviewer.TileFactory;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class BaseOSMProvider {

    private List<String> serverURLs = new ArrayList<>();
    private String name = "Base OSM Provider";

    private final int ZOOM_MIN = 1;
    private final int ZOOM_MAX = 9;
    private final int MAP_ZOOM = 17;
    private final int TILE_SIZE = 256;

    // A property indicating if the X coordinates of tiles go from right to left or left to right. 
    private final boolean XR2L = true;

    // A property indicating if the Y coordinates of tiles go from right to left or left to right.     
    private final boolean YT2B = true;

    public BaseOSMProvider(String name, String url) {
        this.name = name;
        if (url != null) {
            this.serverURLs.add(url);
        }
    }

    public BaseOSMProvider(String name, String[] urls) {
        this.name = name;
        if (urls != null) {
            for (String url : urls) {
                this.serverURLs.add(url);
            }
        }
    }

    public String[] getBaseURLs() {
        return this.serverURLs.toArray(new String[this.serverURLs.size()]);
    }

    public void addBaseURLs(String url) {
        this.serverURLs.add(url);
    }

    public String getName() {
        return this.name;
    }

    public TileFactory getTileFactory() {
        if(!"Local".equals(this.getName())){
        for (String BASE_URL : getBaseURLs()) {
             if (!isAvailableURL(BASE_URL)) {
                continue;
            }
            return new DefaultTileFactory(new OSMTileFactoryInfo(this.getName(), BASE_URL, ZOOM_MIN, ZOOM_MAX, MAP_ZOOM, TILE_SIZE, XR2L, YT2B));  
        
        }  
            return new DefaultTileFactory(new OSMTileFactoryInfo(this.getName(), getBaseURLs()[0], ZOOM_MIN, ZOOM_MAX, MAP_ZOOM, TILE_SIZE, XR2L, YT2B));
        }
        else{
         for (String BASE_URL : getBaseURLs()) {
            
          
             if (!isAvailableURL(BASE_URL)) {
                continue;
            }
            return new DefaultTileFactory(new LocalOSMTileFactoryInfo(this.getName(), BASE_URL, ZOOM_MIN, ZOOM_MAX, MAP_ZOOM, TILE_SIZE, XR2L, YT2B));  
        }  
         return new DefaultTileFactory(new LocalOSMTileFactoryInfo(this.getName(), getBaseURLs()[0], ZOOM_MIN, ZOOM_MAX, MAP_ZOOM, TILE_SIZE, XR2L, YT2B));
        }
    }
    
    

    public boolean isAvailable() {
        for (String urlString : this.getBaseURLs()) {
            if (this.isAvailableURL(urlString)) {
                return true;
            }
        }
        return false;
    }

    public static boolean isAvailableURL(String url) {
        int timeout = 3000;
        url = url.replaceFirst("^https", "http"); // Otherwise an exception may be thrown on invalid SSL certificates.
        try {
            HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
            connection.setConnectTimeout(timeout);
            connection.setReadTimeout(timeout);
            connection.setRequestMethod("HEAD");
            int responseCode = connection.getResponseCode();
            return responseCode == 200 || responseCode == 403;
        } catch (IOException exception) {
            return false;
        }
    }

    public void clearBaseURLs() {
        this.serverURLs.clear();
    }
}
