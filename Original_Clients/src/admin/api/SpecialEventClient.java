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

import admin.types.SpecialEventInfo;
import com.google.gson.reflect.TypeToken;
import common.config.Config;

import java.util.Comparator;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SpecialEventClient extends APIClient<SpecialEventInfo> {

    public SpecialEventClient() {
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<SpecialEventInfo>>() {
        }.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<SpecialEventInfo>>() {
        }.getType();
        this.DATA_TYPE = SpecialEventInfo.class;

        this.URL_DELETE = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_DELETE);
        this.URL_YEARS = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_YEARS);
        this.URL_LIST = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_LIST);
        this.URL_LIST_BY_YEAR = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_LIST_BY_YEAR);
        this.URL_INSERT = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_INSERT);
        this.URL_UPDATE = Config.getAPIUrl(admin.api.ApiURIs.URI.SE_UPDATE);
        this.URL_GET = Config.getAPIUrl(ApiURIs.URI.SE_GET);

        // faverolles 1/15/2020: Adding URL_INSERT_All Initialization
        //  now that the url is being sent from the server and retrieved by getAPIUrl
        this.URL_INSERT_ALL = Config.getAPIUrl(ApiURIs.URI.SE_INSERT_ALL);
    }

    @Override
    protected Comparator<SpecialEventInfo> getComparator() {
        return new Comparator<SpecialEventInfo>() {
            @Override
            public int compare(SpecialEventInfo o1, SpecialEventInfo o2) {
                return o1.name.compareTo(o2.name);
            }
        };
    }
}
