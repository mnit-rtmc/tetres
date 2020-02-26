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

import admin.TeTRESConfig;
import admin.api.ApiURIs;
import common.pyticas.HttpResult;
import common.pyticas.IResponseCallback;
import common.pyticas.HttpClient;
import admin.types.ResponseTTRMSInfo;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TeTRESInfoLoader {

    public interface ICallback {
        public void ready();
        public void fail();
    }

    private static TeTRESInfoLoader _instance = new TeTRESInfoLoader();
    private ApiURIs appURLs;

    private TeTRESInfoLoader() {
    }

    public static TeTRESInfoLoader getInstance() {
        return _instance;
    }

    public ApiURIs getAPIURLs() {
        return this.appURLs;
    }

    public void init(final ICallback callback) {
        HttpClient.get(TeTRESConfig.getAPIUrl(TeTRESConfig.API_TTRMS_INFO), new IResponseCallback<ResponseTTRMSInfo>() {

            @Override
            public void success(ResponseTTRMSInfo result) {
                ApiURIs.URI = result.api_urls;
                TeTRESConfig.dataTypes = result.data_types;
                callback.ready();
            }

            @Override
            public void fail(HttpResult res) {
                throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
            }
        }, ResponseTTRMSInfo.class);
    }
}
