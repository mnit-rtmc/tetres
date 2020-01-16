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
package admin.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.config.Config;
import common.log.TICASLogger;
import common.pyticas.HttpClient;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import admin.TeTRESConfig;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.core.Logger;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;
import common.pyticas.responses.Response;
import common.pyticas.responses.ResponseInteger;
import admin.api.ApiURIs;
import admin.types.ResponseSystemConfigInfo;
import admin.types.SystemConfigInfo;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SystemConfigClient {

    private final String URL_GET;
    private final String URL_UPDATE;
    private final Logger logger;
    private SystemConfigInfo sysConfig;
    

    public SystemConfigClient() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.URL_GET = Config.getAPIUrl(admin.api.ApiURIs.URI.SYSCFG_GET);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SYSCFG_UPDATE);
    }

    public void get(final IHttpResultCallback callback) {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.get_synced(URL_GET);
                try {
                    Gson gsonBuilder = new GsonBuilder().create();
                    ResponseSystemConfigInfo response = gsonBuilder.fromJson(res.contents, ResponseSystemConfigInfo.class);                    
                    sysConfig = response.obj;
                    callback.ready(res);
                } catch(Exception ex) {
                    ex.printStackTrace();
                    callback.fail(res);
                }
            }
        });
    }
    
    public SystemConfigInfo getSystemConfig() {
        return this.sysConfig;
    }
    
    public void update(final SystemConfigInfo cfg, final IHttpResultCallback callback) {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                PostData pd = new PostData();
                pd.addData("cfg", cfg);
                HttpResult res = HttpClient.post_synced(URL_UPDATE, pd);
                if (res.isSuccess()) {
                    Gson gsonBuilder = new GsonBuilder().create();
                    Response response = gsonBuilder.fromJson(res.contents, Response.class);                    
                    if(response.isSuccess()) {
                        callback.ready(res);
                    } else {
                        callback.fail(res);
                    }
                } else {
                    callback.fail(res);
                }
            }
        });
    }    
    
}
