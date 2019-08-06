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
package edu.umn.natsrl.pyticas.restapi;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.sun.net.httpserver.HttpExchange;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.responses.ResponseRoute;
import ticas.common.route.Route;
import java.io.IOException;
import java.io.OutputStream;
import java.util.Map;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RHPOSTString extends POSTRequestHandler {

    private final String response;
    private final ResponseRoute rr;
    private PostData pd;

    public RHPOSTString() {
        rr = new ResponseRoute();
        rr.code = 1;
        rr.message = "success";
        rr.obj = new Route();
        rr.obj.name = "Test Route";
        rr.obj.desc = "This is a test";
        rr.obj.addRNode("rnd_1234");
        rr.obj.addRNode("rnd_5678");
        rr.obj.addRNode("rnd_9101112");
        rr.obj.addRNode("rnd_131415");
        rr.httpResult = null;
        this.response = this.toJson(rr);

        pd = new PostData();
        pd.addData("name", rr.obj.name);
        pd.addData("id", "111");
    }

    @Override
    public void assertResponse(HttpResult res) {
        Gson gsonBuilder = new GsonBuilder().create();
        ResponseRoute obj = gsonBuilder.fromJson(res.contents, ResponseRoute.class);

        System.out.println("  - http_code : " + res.res_code);
        assertTrue(res.res_code == 200);
        System.out.println("  - code : " + obj.code);
        assertEquals(obj.code, this.rr.code);
        System.out.println("  - message : " + obj.message);
        assertEquals(obj.message, this.rr.message);
        System.out.println("  - route : " + obj.obj.toString() + " > " + obj.obj.getRNodeNames().toString());
        assertEquals(obj.obj.name, this.rr.obj.name);
        assertEquals(obj.obj.desc, this.rr.obj.desc);
        assertEquals(obj.obj.getRNodeNames(), this.rr.obj.getRNodeNames());
    }
    
    @Override
    public void handle(HttpExchange t) throws IOException {
        Map<String, String> params = getPostedData(t);
        PostData posted = new PostData();
        for(String key : params.keySet()) {
            posted.addData(key, params.get(key));
        }
        assertEquals(this.pd.getPostDataString(), posted.getPostDataString());
        t.sendResponseHeaders(200, response.length());
        OutputStream os = t.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }

    @Override
    public PostData getPostData() {
        return this.pd;
    }
}
