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
import ticas.tetres.admin.types.SnowRouteInfo;
import java.util.Comparator;

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
        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.SNR_YEARS);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.SNR_LIST);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.SNR_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SNR_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SNR_GET);
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
