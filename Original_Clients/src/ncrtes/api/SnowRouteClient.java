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

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import common.config.Config;
import ncrtes.types.SnowRouteInfo;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import common.pyticas.responses.ResponseInteger;
import common.route.Route;
import java.util.Comparator;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowRouteClient extends APIClient<SnowRouteInfo> {

    public SnowRouteClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<SnowRouteInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<SnowRouteInfo>>(){}.getType();
        this.DATA_TYPE = SnowRouteInfo.class;                
        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.SNR_DELETE);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.SNR_LIST);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.SNR_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SNR_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SNR_GET);                        
    }

    public void list(Integer snrgiId) {
        if (isLoadingList) {
            return;
        }
        PostData pd = new PostData();
        pd.addData("snowroute_group_id", snrgiId);

        isLoadingList = true;
        
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.post_synced(URL_LIST, pd);
                IHttpResultCallback callback = getListCallback();                
                if (res.isSuccess()) {
                    callback.ready(res);
                } else {
                    callback.fail(res);
                }
            }
        });               
    }
    
    public ListResponse<SnowRouteInfo> listSynced(Integer snrgiId) {
        PostData pd = new PostData();
        pd.addData("snowroute_group_id", snrgiId);
        HttpResult res = HttpClient.post_synced(this.URL_LIST, pd);
        if (res.isSuccess()) {
            ListResponse<SnowRouteInfo> obj = gsonBuilder.fromJson(res.contents, RESPONSE_LIST_TYPE);
            obj.httpResult = res;
            return obj;
        } else {
            return null;
        }
    }
    

    public void insert(final SnowRouteInfo wzi, Route r) {
        PostData pd = new PostData();
        pd.addData("data", toJson(wzi));
        pd.addData("route", toJson(r));

        HttpClient.post(this.URL_INSERT, pd, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                if(result.isSuccess()) {
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    fireInsertSuccess(response.obj);
                } else {
                    fireInsertFailed(result, wzi);
                }
            } 

            @Override
            public void fail(HttpResult result) {
                fireInsertFailed(result, wzi);
            }
        });
    }

    @Override
    protected Comparator<SnowRouteInfo> getComparator() {
        return new Comparator<SnowRouteInfo>() {
            @Override
            public int compare(SnowRouteInfo o1, SnowRouteInfo o2) {
                return o1.name.compareTo(o2.name);
            }
        };
    }
}
