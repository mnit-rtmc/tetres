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
package ticas.ncrtes.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ticas.common.config.Config;
import ticas.ncrtes.types.TargetStationManualInfo;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.responses.Response;
import ticas.common.pyticas.responses.ResponseInteger;
import ticas.common.route.Route;
import java.util.Comparator;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ManualTargetStationClient extends APIClient<TargetStationManualInfo> {

    public ManualTargetStationClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<TargetStationManualInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<TargetStationManualInfo>>(){}.getType();
        this.DATA_TYPE = TargetStationManualInfo.class;                
        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.MANUAL_TS_DELETE);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.MANUAL_TS_LIST);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.MANUAL_TS_INSERT);
    }

    public void list(String corridor_name) {
        if (isLoadingList) {
            return;
        }
        PostData pd = new PostData();
        pd.addData("corridor_name", corridor_name);

        isLoadingList = true;
        
        HttpClient.post(this.URL_LIST, pd, getListCallback());
    }
    
    public ListResponse<TargetStationManualInfo> listSynced(String corridor_name) {
        PostData pd = new PostData();
        pd.addData("corridor_name", corridor_name);
        HttpResult res = HttpClient.post_synced(this.URL_LIST, pd);
        if (res.isSuccess()) {
            ListResponse<TargetStationManualInfo> obj = gsonBuilder.fromJson(res.contents, RESPONSE_LIST_TYPE);
            obj.httpResult = res;
            return obj;
        } else {
            return null;
        }
    }
    

    public void insert(final TargetStationManualInfo tsmi) {
        PostData pd = new PostData();
        pd.addData("data", toJson(tsmi));

        HttpClient.post(this.URL_INSERT, pd, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                if(result.isSuccess()) {
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    fireInsertSuccess(response.obj);
                } else {
                    fireInsertFailed(result, tsmi);
                }
            } 

            @Override
            public void fail(HttpResult result) {
                fireInsertFailed(result, tsmi);
            }
        });
    }

    @Override
    protected Comparator<TargetStationManualInfo> getComparator() {
        return new Comparator<TargetStationManualInfo>() {
            @Override
            public int compare(TargetStationManualInfo o1, TargetStationManualInfo o2) {
                return o1.station_id.compareTo(o2.station_id);
            }
        };
    }
}
