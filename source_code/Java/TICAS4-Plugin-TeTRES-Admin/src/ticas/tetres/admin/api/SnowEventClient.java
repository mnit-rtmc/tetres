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
import ticas.tetres.admin.types.SnowEventInfo;
import java.util.Comparator;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowEventClient extends APIClient<SnowEventInfo> {
    
    public SnowEventClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<SnowEventInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<SnowEventInfo>>(){}.getType();
        this.DATA_TYPE = SnowEventInfo.class;        
        
        this.URL_DELETE = Config.getAPIUrl(ApiURIs.URI.SNE_DELETE);
        this.URL_YEARS = Config.getAPIUrl(ApiURIs.URI.SNE_YEARS);
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.SNE_LIST);
        this.URL_LIST_BY_YEAR = Config.getAPIUrl(ApiURIs.URI.SNE_LIST_BY_YEAR);
        this.URL_INSERT = Config.getAPIUrl(ApiURIs.URI.SNE_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(ApiURIs.URI.SNE_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SNE_GET);
    }   

    @Override
    protected Comparator<SnowEventInfo> getComparator() {
        return new Comparator<SnowEventInfo>() {
            @Override
            public int compare(SnowEventInfo o1, SnowEventInfo o2) {
                return o1.start_time.compareTo(o2.start_time);
            }
        };
    }
}
