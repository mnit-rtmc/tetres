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

import com.sun.net.httpserver.HttpExchange;
import ticas.common.pyticas.HttpResult;
import java.io.IOException;
import java.io.OutputStream;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.assertTrue;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RHGETString extends GETRequestHandler {

    private final String response;

    public RHGETString() {
        this.response = "TEST";
    }

    @Override
    public void assertResponse(HttpResult res) {
        System.out.println("  - http_code : " + res.res_code);
        assertTrue(res.res_code == 200);
        System.out.println("  - response_text : " + res.contents);
        assertTrue("TEST".equals(res.contents));
    }

    @Override
    public void handle(HttpExchange t) throws IOException {
        t.sendResponseHeaders(200, response.length());
        OutputStream os = t.getResponseBody();
        os.write(response.getBytes());
        os.close();
    }
}
