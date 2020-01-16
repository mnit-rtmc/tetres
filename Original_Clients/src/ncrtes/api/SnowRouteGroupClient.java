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
package ncrtes.api;

import com.google.gson.reflect.TypeToken;
import common.config.Config;
import ncrtes.types.SnowRouteGroupInfo;
import common.pyticas.HttpClient;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import common.pyticas.responses.ResponseInteger;
import java.util.Comparator;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowRouteGroupClient extends APIClient<SnowRouteGroupInfo> {
    
    private String URL_COPY = "";
    
    public SnowRouteGroupClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<SnowRouteGroupInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<SnowRouteGroupInfo>>(){}.getType();
        this.DATA_TYPE = SnowRouteGroupInfo.class;                
        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_DELETE);
        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_YEARS);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_LIST);
        this.URL_LIST_BY_YEAR = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_LIST_BY_YEAR);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_GET);
        this.URL_COPY = Config.getAPIUrl(ApiURIs.URI.SNR_GROUP_COPY);
    }   
    
    public void copy(SnowRouteGroupInfo exData, final SnowRouteGroupInfo newData) {
        PostData pd = new PostData();
        pd.addData("snowroute_group_id", exData.id);
        pd.addData("data", newData);
        HttpClient.post(this.URL_COPY, pd, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {                
                if (result.isSuccess()) {
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    if(response.isSuccess())
                        fireCopySuccess(response.obj);
                    else
                        fireCopyFailed(result, newData);
                } else {
                    fireCopyFailed(result, newData);
                }
            }

            @Override
            public void fail(HttpResult result) {
                fireUpdateFailed(result, newData);
            }
        });
    }
    

    @Override
    protected Comparator<SnowRouteGroupInfo> getComparator() {
        return new Comparator<SnowRouteGroupInfo>() {
            @Override
            public int compare(SnowRouteGroupInfo o1, SnowRouteGroupInfo o2) {
                return o1.name.compareTo(o2.name);
            }
        };
    }
}
