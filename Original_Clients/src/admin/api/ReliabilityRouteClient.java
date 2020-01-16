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
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import common.route.Route;
import admin.api.APIClient;
import admin.api.ApiURIs;
import admin.api.ListResponse;
import admin.api.ObjectResponse;
import admin.types.ReliabilityRouteInfo;
import java.lang.reflect.Type;
import java.util.Comparator;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ReliabilityRouteClient extends APIClient<ReliabilityRouteInfo> {

    public ReliabilityRouteClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<ReliabilityRouteInfo>>() {}.getType();
        this.RESPONSE_TYPE = new TypeToken<admin.api.ObjectResponse<ReliabilityRouteInfo>>() {}.getType();
        this.DATA_TYPE = ReliabilityRouteInfo.class;
        this.URL_DELETE = Config.getAPIUrl(admin.api.ApiURIs.URI.TTROUTE_DELETE);
        this.URL_LIST = Config.getAPIUrl(admin.api.ApiURIs.URI.TTROUTE_LIST);
        this.URL_INSERT = Config.getAPIUrl(admin.api.ApiURIs.URI.TTROUTE_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(admin.api.ApiURIs.URI.TTROUTE_UPDATE);
        this.URL_GET = Config.getAPIUrl(admin.api.ApiURIs.URI.TTROUTE_GET);
    }

    @Override
    public void listByYear(Integer year) {
        this.notSupportedAPI("TTRouteClient.listByYear()");
    }

    @Override
    public void years() {
        this.notSupportedAPI("TTRouteClient.years()");
    }
    
    public Route opposingRoute(int id) {
        PostData pd = new PostData();
        pd.addData("id", id);
        Type rtype = new TypeToken<admin.api.ObjectResponse<Route>>() {
        }.getType();
        ObjectResponse<Route> res = HttpClient.post_synced(Config.getAPIUrl(ApiURIs.URI.TTROUTE_OPPOSITE_ROUTE), pd, rtype);
        if (res != null) {
            return res.obj;
        } else {
            return null;
        }
    }

    @Override
    protected Comparator<ReliabilityRouteInfo> getComparator() {
        return new Comparator<ReliabilityRouteInfo>() {
            @Override
            public int compare(ReliabilityRouteInfo o1, ReliabilityRouteInfo o2) {
                return o1.name.compareTo(o2.name);
            }
        };
    }
}
