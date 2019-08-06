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
package ticas.common.pyticas;

import ticas.common.log.TICASLogger;
import org.apache.logging.log4j.Logger;

/**
 *
 * @author Chongmyung
 */
public class RestClientWorker extends Thread {

    private String USER_AGENT = "TICAS4 Client";
    private final IHttpResultCallback httpResultCallback;
    private String target_url;
    private PostData postData;
    private org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(RestClientWorker.class.getName());

    public RestClientWorker(String target_url, IHttpResultCallback httpResultCallback) {
        this.target_url = target_url;
        this.httpResultCallback = httpResultCallback;
    }

    public RestClientWorker(String uri_path, PostData pd, IHttpResultCallback httpResultCallback) {
        this.target_url = uri_path;
        this.postData = pd;
        this.httpResultCallback = httpResultCallback;
    }

    private void get() {
        HttpResult res = HttpClient.get_synced(this.target_url);
        if (this.httpResultCallback != null && res.res_code == 200) {
            this.httpResultCallback.ready(res);
        } else {
            this.httpResultCallback.fail(res);
        }
    }

    private void post() {
        HttpResult res = HttpClient.post_synced(this.target_url, this.postData);
        if (this.httpResultCallback != null && res.res_code == 200) {
            this.httpResultCallback.ready(res);
        } else {
            this.httpResultCallback.fail(res);
        }
    }

    @Override
    public void run() {
        if (this.postData != null) {
            this.post();
        } else {
            this.get();
        }
    }
}
