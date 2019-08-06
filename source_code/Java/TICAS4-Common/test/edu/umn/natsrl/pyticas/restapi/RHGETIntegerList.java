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
import ticas.common.pyticas.responses.ResponseIntegerList;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RHGETIntegerList extends GETRequestHandler {

    private final String response;
    private final ResponseIntegerList ril;

    public RHGETIntegerList() {
        ril = new ResponseIntegerList();
        ril.code = 1;
        ril.message = "success";
        ril.obj = new ArrayList<Integer>();
        ril.obj.add(100);
        ril.obj.add(200);
        ril.obj.add(300);
        ril.httpResult = null;
        this.response = this.toJson(ril);
    }

    @Override
    public void assertResponse(HttpResult res) {
        Gson gsonBuilder = new GsonBuilder().create();
        ResponseIntegerList obj = gsonBuilder.fromJson(res.contents, ResponseIntegerList.class);

        System.out.println("  - http_code : " + res.res_code);
        assertTrue(res.res_code == 200);
        System.out.println("  - code : " + obj.code);
        assertEquals(obj.code, this.ril.code);
        System.out.println("  - message : " + obj.message);
        assertEquals(obj.message, this.ril.message);
        System.out.println("  - list : " + obj.obj.toString());
        assertEquals(obj.obj, this.ril.obj);
    }

    @Override
    public void handle(HttpExchange t) throws IOException {
        t.sendResponseHeaders(200, response.length());
        OutputStream os = t.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }
}
