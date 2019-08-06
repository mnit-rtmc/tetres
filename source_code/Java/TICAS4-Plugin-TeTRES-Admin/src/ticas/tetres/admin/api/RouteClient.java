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
package ticas.tetres.admin.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import java.io.DataInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import ticas.common.config.Config;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.xml.bind.DatatypeConverter;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.IResponseCallback;
import ticas.common.pyticas.RunningDialog;
import ticas.common.pyticas.responses.ResponseRoute;
import ticas.common.pyticas.responses.ResponseString;
import ticas.common.route.Route;
import ticas.common.util.FileHelper;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteClient {

    private final String URL_ROUTE_FROM_CFG;
    private final String URL_ROUTE_XLSX;

    public RouteClient() {
        this.URL_ROUTE_FROM_CFG = Config.getAPIUrl(ApiURIs.URI.ROUTE_FROM_CFG);
        this.URL_ROUTE_XLSX = Config.getAPIUrl(ApiURIs.URI.ROUTE_XLSX);
    }

    public void getFromRouteConfig(final String filepath, final IResponseCallback<ResponseRoute> callback) {

        RunningDialog.run(new ticas.common.pyticas.IRequest() {
            @Override
            public void request() {
                try {
                    // read file
                    File file = new File(filepath);
                    byte[] fileData = new byte[(int) file.length()];
                    DataInputStream dis = new DataInputStream(new FileInputStream(file));
                    dis.readFully(fileData);
                    dis.close();

                    // bas64 encoding
                    String base64Encoded = DatatypeConverter.printBase64Binary(fileData);

                    // pack to PostData
                    PostData pd = new PostData();
                    pd.addData("cfgfile", base64Encoded);

                    // call
                    HttpResult res = HttpClient.post_synced(URL_ROUTE_FROM_CFG, pd);
                    if (res.isSuccess()) {
                        Gson gsonBuilder = new GsonBuilder().create();
                        ResponseRoute obj = gsonBuilder.fromJson(res.contents, ResponseRoute.class);
                        obj.httpResult = res;
                        if(obj.isSuccess()) {
                            callback.success(obj);
                        } else {
                            callback.fail(res);
                        }
                    } else {
                        callback.fail(res);
                    }
                } catch (FileNotFoundException ex) {
                    Logger.getLogger(RouteClient.class.getName()).log(Level.SEVERE, null, ex);
                } catch (IOException ex) {
                    Logger.getLogger(RouteClient.class.getName()).log(Level.SEVERE, null, ex);
                } 
            }
        });
    }

    public void getXlsxContent(final Route route, final IResponseCallback<ResponseString> responseCallback) {
        
        RunningDialog.run(new ticas.common.pyticas.IRequest() {
            @Override
            public void request() {
                // pack to PostData
                PostData pd = new PostData();
                pd.addData("route", route);

                // call
                HttpResult res = HttpClient.post_synced(URL_ROUTE_XLSX, pd);
                if (res.isSuccess()) {
                    Gson gsonBuilder = new GsonBuilder().create();
                    ResponseString response = gsonBuilder.fromJson(res.contents, ResponseString.class);
                    response.httpResult = res;
                    if(response.isSuccess()) {
                        responseCallback.success(response);
                    } else {
                        responseCallback.fail(res);
                    }
                } else {
                    responseCallback.fail(res);
                }
            }
        });
    }
    
    public void saveRouteConfig(Route route, final String filepath_rcfg, final IHttpResultCallback httpResultCallback) {
        getXlsxContent(route, new IResponseCallback<ResponseString>() {
            @Override
            public void success(ResponseString result) {
                byte[] decodedString = Base64.getDecoder().decode(result.obj.getBytes(StandardCharsets.UTF_8));
                try {
                    FileHelper.writeBinaryFile(decodedString, filepath_rcfg);
                } catch (IOException ex) {
                    Logger.getLogger(RouteClient.class.getName()).log(Level.SEVERE, null, ex);
                    httpResultCallback.fail(result.httpResult);
                }
                httpResultCallback.ready(result.httpResult);
            }

            @Override
            public void fail(HttpResult result) {
                httpResultCallback.fail(result);
            }
        });
    }    
}
