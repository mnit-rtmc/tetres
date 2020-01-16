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
import common.infra.Infra;
import common.infra.RNode;
import ncrtes.types.TargetStationInfo;
import common.pyticas.HttpResult;
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import java.util.Comparator;
import common.pyticas.IHttpResultCallback;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TargetStationClient extends APIClient<TargetStationInfo> {

    public TargetStationClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<TargetStationInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<TargetStationInfo>>(){}.getType();
        this.DATA_TYPE = TargetStationInfo.class;                
        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.TS_DELETE);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.TS_LIST);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.TS_UPDATE);
        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.TS_YEARS);
    }

    public void list(Integer year, String corridor_name) {
        if (isLoadingList) {
            return;
        }
        PostData pd = new PostData();
        pd.addData("year", year);
        pd.addData("corridor_name", corridor_name);

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
    
    public ListResponse<TargetStationInfo> listSynced(Integer year, String corridor_name) {
        PostData pd = new PostData();
        pd.addData("year", year);
        pd.addData("corridor_name", corridor_name);
        HttpResult res = HttpClient.post_synced(this.URL_LIST, pd);
        if (res.isSuccess()) {
            ListResponse<TargetStationInfo> obj = gsonBuilder.fromJson(res.contents, RESPONSE_LIST_TYPE);
            obj.httpResult = res;
            return obj;
        } else {
            return null;
        }
    }
    
    @Override
    protected Comparator<TargetStationInfo> getComparator() {
        return new Comparator<TargetStationInfo>() {            
            @Override
            public int compare(TargetStationInfo o1, TargetStationInfo o2) {
                RNode rn1 = Infra.getInstance().getRNode(o1.station_id);
                RNode rn2 = Infra.getInstance().getRNode(o2.station_id);
                return rn1.order.compareTo(rn2.order);
            }
        };
    }
}
