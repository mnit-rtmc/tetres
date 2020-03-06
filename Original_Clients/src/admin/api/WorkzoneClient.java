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

import com.google.gson.reflect.TypeToken;
import common.config.Config;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import common.pyticas.responses.ResponseInteger;
import common.route.Route;
import admin.api.APIClient;
import admin.api.ApiURIs;
import admin.api.ListResponse;
import admin.api.ObjectResponse;
import admin.types.WorkZoneInfo;
import java.util.Comparator;
import java.util.Timer;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;
import admin.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class WorkzoneClient extends APIClient<WorkZoneInfo> {

    public WorkzoneClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<WorkZoneInfo>>() {
        }.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<WorkZoneInfo>>() {
        }.getType();
        this.DATA_TYPE = WorkZoneInfo.class;

        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.WZ_DELETE);
//        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.WZ_YEARS);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.WZ_LIST);
//        this.URL_LIST_BY_YEAR = Config.getAPIUrl(ApiURIs.URI.WZ_LIST_BY_YEAR);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.WZ_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.WZ_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.WZ_GET);
    }

    public void list(Integer wzGroupId) {
        if (isLoadingList) {
            return;
        }
        final PostData pd = new PostData();
        pd.addData("wzgroup_id", wzGroupId);

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

//    public HttpResult insert(Route obj) {
//        PostData pd = new PostData();
//        pd.addData("data", toJson(obj));
//        HttpResult res = RestClient.post_synced(this.URL_INSERT, pd);
//        return res;
//    }
    public void insert(final WorkZoneInfo wzi, Route r) {
        final PostData pd = new PostData();
        pd.addData("data", toJson(wzi));
        pd.addData("route", toJson(r));

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult result = HttpClient.post_synced(URL_INSERT, pd);
                if (result.isSuccess()) {
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    if (response.isSuccess()) {
                        fireInsertSuccess(response.obj);
                    } else {
                        fireInsertFailed(result, wzi);
                    }
                } else {
                    fireInsertFailed(result, wzi);
                }
            }
        });
    }

    @Override
    protected Comparator<WorkZoneInfo> getComparator() {
        return new Comparator<WorkZoneInfo>() {
            @Override
            public int compare(WorkZoneInfo o1, WorkZoneInfo o2) {
                return o1.getName().compareTo(o2.getName());
            }
        };
    }
}
