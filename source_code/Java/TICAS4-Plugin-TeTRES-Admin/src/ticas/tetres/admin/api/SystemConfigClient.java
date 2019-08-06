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
import ticas.common.config.Config;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.PostData;
import ticas.tetres.admin.TeTRESConfig;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.core.Logger;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;
import ticas.common.pyticas.responses.Response;
import ticas.common.pyticas.responses.ResponseInteger;
import ticas.tetres.admin.types.ResponseSystemConfigInfo;
import ticas.tetres.admin.types.SystemConfigInfo;

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
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SYSCFG_GET);
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
