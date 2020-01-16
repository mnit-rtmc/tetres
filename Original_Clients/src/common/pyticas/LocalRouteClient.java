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
package common.pyticas;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import common.config.Config;
import common.log.TICASLogger;
import common.pyticas.responses.ResponseRoute;
import common.route.Route;
import java.util.List;
import javax.swing.JOptionPane;

import common.route.IRouteChanged;
import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.bind.DatatypeConverter;

import common.pyticas.responses.ResponseString;
import common.util.FileHelper;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class LocalRouteClient {

    private static LocalRouteClient _instance = new LocalRouteClient();
    private List<IRouteChanged> changeListeners = new ArrayList<IRouteChanged>();
    private List<Route> routeList = new ArrayList<Route>();
    private boolean isLoading = false;
    private static final Map<String, Route> ROUTE_CACHE = new HashMap<String, Route>();

    public static LocalRouteClient getInstance() {
        return _instance;
    }
    
    public void addChangeListener(IRouteChanged listener) {
        changeListeners.add(listener);
    }    
    
    /**
     * Save `Route` to the cache directory
     * 
     * @param r
     */
    public boolean saveRoute(Route r) {
        return Route.saveRoute(r);
    }
        
    public void loadList() {

        if (isLoading) {
            return;
        }
        routeList.clear();
        isLoading = true;
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                List<String> fileList = Route.getRouteFiles(false);
                for (String filepath : fileList) {
                    Route r = getRouteFromRouteFile(filepath);
                    if (r != null) {
                        routeList.add(r);
                    }
                }
                for (IRouteChanged listener : changeListeners) {
                    TICASLogger.getLogger(LocalRouteClient.class.getName()).info("calling route change listener");
                    listener.routeChanged(routeList);
                }
                isLoading = false;
            }
        });
    }
    
    /**
     * Get `Route` object with the given route name (from the cache directory)
     * @param routeName
     * @return
     */
    public Route getRoute(String routeName) {
        return getRouteFromRouteFile(Route.getFilePath(routeName));
    }
    
    public void deleteRoute(String routeName) {
        String routeFilePath = Route.getFilePath(routeName);
        File file = new File(routeFilePath);
        if (!file.exists()) {
            JOptionPane.showMessageDialog(null, "Route file does not exist");
            return;
        }
        file.delete();
        if (ROUTE_CACHE.containsKey(routeFilePath)) {
            ROUTE_CACHE.remove(routeFilePath);
        }
    }    
    
    public void getRouteFromXlsxFile(final String xlsxFilePath, final IRouteCallback callback) {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                callback.callback(getRouteFromXlsxFileSynced(xlsxFilePath));
            }
        });
    }
    
    public void deleteRoute(Route r) {
        deleteRoute(r.name);
    }    
    
    public Route getRouteFromRouteFile(String routeFilePath) {
        try {
            return Route.load(routeFilePath);
        } catch (IOException ex) {
            Logger.getLogger(LocalRouteClient.class.getName()).log(Level.SEVERE, null, ex);
            return null;
        }
    }
    
    public Route getRouteFromXlsxFileSynced(String xlsxFilePath) {
        try {
            // read file
            File file = new File(xlsxFilePath);
            byte[] fileData = new byte[(int) file.length()];
            DataInputStream dis = new DataInputStream(new FileInputStream(file));
            dis.readFully(fileData);
            dis.close();

            // bas64 encoding
            String base64Encoded = DatatypeConverter.printBase64Binary(fileData);

            // pack to PostData
            PostData pd = new PostData();
            pd.addData("xlsxcontent", base64Encoded);

            // call
            HttpResult res = HttpClient.post_synced(Config.getAPIUrl(ApiURIs.URI.ROUTE_FROM_XLSX), pd);
            if (res.isSuccess()) {
                Gson gsonBuilder = new GsonBuilder().create();
                ResponseRoute obj = gsonBuilder.fromJson(res.contents, ResponseRoute.class);
                return obj.obj;
            }
        } catch (FileNotFoundException ex) {
            Logger.getLogger(LocalRouteClient.class.getName()).log(Level.SEVERE, null, ex);
        } catch (IOException ex) {
            Logger.getLogger(LocalRouteClient.class.getName()).log(Level.SEVERE, null, ex);
        } catch(Exception ex) {
            Logger.getLogger(LocalRouteClient.class.getName()).log(Level.SEVERE, null, ex);
        }
        return null;
    }
       
    public byte[] getXlsxContentSynced(Route route) {

        // pack to PostData
        PostData pd = new PostData();
        pd.addData("route", route);

        // call
        HttpResult res = HttpClient.post_synced(Config.getAPIUrl(ApiURIs.URI.ROUTE_TO_XLSX), pd);
        if (res.isSuccess()) {
            Gson gsonBuilder = new GsonBuilder().create();
            ResponseString response = gsonBuilder.fromJson(res.contents, ResponseString.class);
            response.httpResult = res;
            if (response.isSuccess()) {
                return Base64.getDecoder().decode(response.obj.getBytes(StandardCharsets.UTF_8));
            }
        }
        return null;
    }
 
    public void saveRouteXlsxFile(Route route, String xlsxFilePathToBeSaved, IBooleanCallback callback) {
        byte[] xlsxContent = getXlsxContentSynced(route);
        if(xlsxContent == null || xlsxContent.length == 0) {
            callback.callback(false, "Cannot make XLSX file");
        }
        try {
            FileHelper.writeBinaryFile(xlsxContent, xlsxFilePathToBeSaved);
            callback.callback(true, "");
        } catch (IOException ex) {
            Logger.getLogger(Route.class.getName()).log(Level.SEVERE, null, ex);
            callback.callback(false, "");
        }
    }

    /**
     * Update lane configuration of the given route as the given xlsx file
     * @param r
     * @param xlsxFilePath
     * @param callback
     */
    public void updateRouteConfig(String routeName, String xlsxFilePath, final IBooleanCallback callback) {        
        if(!(new File(Route.getFilePath(routeName))).exists()) {
            callback.callback(false, "The given route does not exist");
            return;
        }
        getRouteFromXlsxFile(xlsxFilePath, new IRouteCallback() {
            @Override
            public void callback(Route r) {                
                if(saveRoute(r)) {
                    callback.callback(true, "");
                } else {
                    callback.callback(false, "");
                }
                
            }
        });
        
    }

}
