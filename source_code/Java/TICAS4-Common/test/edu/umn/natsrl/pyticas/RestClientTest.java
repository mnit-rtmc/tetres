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
package edu.umn.natsrl.pyticas;

import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.PostData;
import com.sun.net.httpserver.HttpServer;
import edu.umn.natsrl.pyticas.restapi.RHGETIntegerList;
import edu.umn.natsrl.pyticas.restapi.RHGETRoute;
import edu.umn.natsrl.pyticas.restapi.RHGETString;
import edu.umn.natsrl.pyticas.restapi.GETRequestHandler;
import edu.umn.natsrl.pyticas.restapi.POSTRequestHandler;
import edu.umn.natsrl.pyticas.restapi.RHPOSTString;
import java.io.IOException;
import java.net.InetSocketAddress;
import java.util.HashMap;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RestClientTest {

    HashMap<String, GETRequestHandler> GET_EntryPoints = new HashMap<>();
    HashMap<String, POSTRequestHandler> POST_EntryPoints = new HashMap<>();
    
    int port = 8000;
    private HttpServer server;

    public RestClientTest() throws IOException {
        GET_EntryPoints.put("/get_test", new RHGETString());
        GET_EntryPoints.put("/get_integer_list", new RHGETIntegerList());
        GET_EntryPoints.put("/get_route", new RHGETRoute());
        
        POST_EntryPoints.put("/post_string", new RHPOSTString());
              
    }

    @BeforeClass
    public static void setUpClass() throws IOException {

    }

    @AfterClass
    public static void tearDownClass() {
    }

    @Before
    public void setUp() throws IOException {
        InetSocketAddress address = new InetSocketAddress(port);
        server = HttpServer.create(address, 0);
        for (String uri : GET_EntryPoints.keySet()) {
            server.createContext(uri, GET_EntryPoints.get(uri));
        }
        for (String uri : POST_EntryPoints.keySet()) {
            server.createContext(uri, POST_EntryPoints.get(uri));
        }        
        server.setExecutor(null);
        server.start();         
    }

    @After
    public void tearDown() {
        this.server.stop(0);
    }

    /**
     * Test of get_synced method, of class RestClient.
     */
    @Test
    public void testGet_synced() throws Exception {
        System.out.println("get_synced");
        String base_url = "http://localhost:" + this.port;
        for (String uri : this.GET_EntryPoints.keySet()) {
            String target_url = base_url + uri;
            System.out.println("checking : \"" + uri + "\"");
            HttpResult res = HttpClient.get_synced(target_url);
            GETRequestHandler checker = this.GET_EntryPoints.get(uri);
            checker.assertResponse(res);
        }

    }

        /**
     * Test of post_synced method, of class RestClient.
     */
    @Test
    public void testPost_synced() throws Exception {
        System.out.println("post_synced");
        String base_url = "http://localhost:" + this.port;
        for (String uri : this.POST_EntryPoints.keySet()) {
            String target_url = base_url + uri;
            POSTRequestHandler checker = this.POST_EntryPoints.get(uri);            
            System.out.println("checking : \"" + uri + "\"");
            PostData pd = checker.getPostData();
            HttpResult res = HttpClient.post_synced(target_url, pd);
            checker.assertResponse(res);
        }
    }
}
