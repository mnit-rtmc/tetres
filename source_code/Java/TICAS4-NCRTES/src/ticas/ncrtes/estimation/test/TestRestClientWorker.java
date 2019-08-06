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
package ticas.ncrtes.estimation.test;

import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.PostData;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class TestRestClientWorker extends Thread {

    private String USER_AGENT = "TICAS4 Client";
    private final IHttpCallback httpResultCallback;
    private String target_url;
    private PostData postData;

    public TestRestClientWorker(String target_url, IHttpCallback httpResultCallback) {
        this.target_url = target_url;
        this.httpResultCallback = httpResultCallback;
    }

    public TestRestClientWorker(String uri_path, PostData pd, IHttpCallback httpResultCallback) {
        this.target_url = uri_path;
        this.postData = pd;
        this.httpResultCallback = httpResultCallback;
    }

    private void post() {
        TestEstimation.post_synced(this.target_url, this.postData, this.httpResultCallback);
    }

    @Override
    public void run() {
        this.post();
    }
}
