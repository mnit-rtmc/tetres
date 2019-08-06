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

import com.google.gson.reflect.TypeToken;
import ticas.common.config.Config;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.tetres.admin.types.SnowManagementInfo;
import java.util.Comparator;
import java.util.Timer;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;
import ticas.tetres.admin.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowManagementClient extends APIClient<SnowManagementInfo> {

    public SnowManagementClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<SnowManagementInfo>>() {
        }.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<SnowManagementInfo>>() {
        }.getType();
        this.DATA_TYPE = SnowManagementInfo.class;

        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.SNM_DELETE);
        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.SNM_YEARS);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.SNM_LIST);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.SNM_INSERT);
        this.URL_INSERT_ALL = Config.getAPIUrl(ApiURIs.URI.SNM_INSERT_ALL);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SNM_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SNM_GET);
    }

    public void list(Integer snowEventId) {
        if (isLoadingList) {
            return;
        }
        final PostData pd = new PostData();
        pd.addData("snowevent_id", snowEventId);

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

    @Override
    protected Comparator<SnowManagementInfo> getComparator() {
        return new Comparator<SnowManagementInfo>() {
            @Override
            public int compare(SnowManagementInfo o1, SnowManagementInfo o2) {
                return o1.getDuration().compareTo(o2.getDuration());
            }
        };
    }

}
