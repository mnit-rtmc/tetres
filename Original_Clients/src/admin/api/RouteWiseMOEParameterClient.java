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
import java.util.Comparator;
import admin.types.RouteWiseMOEParameterInfo;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteWiseMOEParameterClient extends APIClient<RouteWiseMOEParameterInfo> {

    public RouteWiseMOEParameterClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<RouteWiseMOEParameterInfo>>() {
        }.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<RouteWiseMOEParameterInfo>>() {
        }.getType();
        this.DATA_TYPE = RouteWiseMOEParameterInfo.class;

        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.RW_MOE_PARAM_LIST);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.RW_MOE_PARAM_INSERT);
    }

    @Override
    protected Comparator<RouteWiseMOEParameterInfo> getComparator() {
        return new Comparator<RouteWiseMOEParameterInfo>() {
            @Override
            public int compare(RouteWiseMOEParameterInfo o1, RouteWiseMOEParameterInfo o2) {
                return o1.update_time.compareTo(o2.update_time);
            }
        };
    }}
