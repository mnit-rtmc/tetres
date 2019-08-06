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

import ticas.ncrtes.api.ApiURIs;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IResponseCallback;
import ticas.common.pyticas.HttpClient;
import ticas.ncrtes.types.ResponseNCRTESInfo;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class NCRTESInfoLoader {

    public interface ICallback {
        public void ready();
        public void fail();
    }

    private static NCRTESInfoLoader _instance = new NCRTESInfoLoader();
    private ApiURIs appURLs;

    private NCRTESInfoLoader() {
    }

    public static NCRTESInfoLoader getInstance() {
        return _instance;
    }

    public ApiURIs getAPIURLs() {
        return this.appURLs;
    }

    public void init(final ICallback callback) {
        HttpClient.get(NCRTESConfig.getAPIUrl(NCRTESConfig.API_NCRTES_INFO), new IResponseCallback<ResponseNCRTESInfo>() {

            @Override
            public void success(ResponseNCRTESInfo result) {
                ApiURIs.URI = result.api_urls;
                NCRTESConfig.dataTypes = result.data_types;
                callback.ready();
            }

            @Override
            public void fail(HttpResult res) {
                throw new UnsupportedOperationException("Not supported yet."); //To change body of generated methods, choose Tools | Templates.
            }
        }, ResponseNCRTESInfo.class);
    }
}
