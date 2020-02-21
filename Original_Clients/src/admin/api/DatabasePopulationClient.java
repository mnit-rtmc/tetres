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

import admin.types.DatabasePopulationInfo;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.config.Config;
import common.pyticas.HttpClient;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.RunningDialog;


public class DatabasePopulationClient {

  private final String URL_GET;
  private DatabasePopulationInfo popInfo;

  public DatabasePopulationInfo getPopInfo() {
    return this.popInfo;
  }

  public DatabasePopulationClient() {
    this.URL_GET = Config.getAPIUrl("/api-extension/current-database-population");
  }

  public void get(final IHttpResultCallback callback) {
    RunningDialog.run(() -> {
      HttpResult res = HttpClient.get_synced(URL_GET);
      try {
        Gson gsonBuilder = new GsonBuilder().create();
        popInfo = gsonBuilder.fromJson(res.contents, DatabasePopulationInfo.class);
        callback.ready(res);
      } catch (Exception ex) {
        ex.printStackTrace();
        callback.fail(res);
      }
    });
  }
}
