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
package ticas.common.infra;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.config.Config;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.ApiURIs;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.HttpClient;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class InfraLoader {

    public static void load(final IHttpResultCallback callback) {
        HttpClient.get(Config.getAPIUrl(ApiURIs.INFO_INFRA), new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                Gson gsonBuilder = new GsonBuilder().create();
                Infra infra = Infra.getInstance();
                InfraInfo infraInfo = gsonBuilder.fromJson(res.contents, InfraInfo.class);
                infra.setInfraInfo(infraInfo);
                if (callback != null) {
                    callback.ready(res);
                }
            }

            @Override
            public void fail(HttpResult res) {
            }
        });
    }

    public static boolean load() {
        HttpResult res = HttpClient.get_synced(Config.getAPIUrl("/ticas/infra"));
        if(res.res_code != 200) {
            Infra infra = Infra.getInstance();
            infra.setFailToLoadInfra(true);            
            return false;
        }
        try {
            Gson gsonBuilder = new GsonBuilder().create();
            Infra infra = Infra.getInstance();
            InfraInfo infraInfo = gsonBuilder.fromJson(res.contents, InfraInfo.class);
            infra.setInfraInfo(infraInfo);
            return true;
        } catch(Exception ex) {
            TICASLogger.getLogger(InfraLoader.class.getName()).error(String.format("could not load roadway network information : %s", ex.getMessage()));
            Infra infra = Infra.getInstance();
            infra.setFailToLoadInfra(true);
            return false;
        }
    }
}
