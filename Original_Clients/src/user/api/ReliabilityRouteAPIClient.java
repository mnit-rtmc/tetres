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
package user.api;

import com.google.gson.reflect.TypeToken;
import common.config.Config;
import common.infra.Corridor;
import common.pyticas.HttpClient;
import common.pyticas.PostData;
import user.types.ReliabilityRouteInfo;

import java.util.Comparator;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ReliabilityRouteAPIClient extends APIClient<ReliabilityRouteInfo> {

    public ReliabilityRouteAPIClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<ReliabilityRouteInfo>>() {
        }.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<ReliabilityRouteInfo>>() {
        }.getType();
        this.DATA_TYPE = ReliabilityRouteInfo.class;
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.ROUTE_LIST);
    }

    @Override
    public void listByYear(Integer year) {
        this.notSupportedAPI("ReliabilityRoute.listByYear()");
    }

    @Override
    public void years() {
        this.notSupportedAPI("ReliabilityRoute.years()");
    }

    public void listByCorridor(Corridor corridor) {
        if (isLoadingList) {
            return;
        }
        PostData pd = new PostData();
        pd.addData("corridor", corridor.name);

        isLoadingList = true;
        HttpClient.post(this.URL_LIST, pd, getListCallback());
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
