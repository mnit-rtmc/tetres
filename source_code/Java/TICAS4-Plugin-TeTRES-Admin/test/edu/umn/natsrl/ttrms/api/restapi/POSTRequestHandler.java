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
package edu.umn.natsrl.ttrms.api.restapi;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import ticas.common.pyticas.PostData;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public abstract class POSTRequestHandler implements ResponseChecker, HttpHandler {

    public String toJson(Object obj) {
        Gson gsonBuilder = new GsonBuilder().create();
        return gsonBuilder.toJson(obj);
    }

    public static Map<String, String> getQueryMap(String query) {
        String[] params = query.split("&");
        Map<String, String> map = new HashMap<String, String>();
        for (String param : params) {
            String name = param.split("=")[0];
            String value = param.split("=")[1];
            try {
                map.put(name, URLDecoder.decode(value, "UTF-8"));
            } catch (UnsupportedEncodingException ex) {
                Logger.getLogger(POSTRequestHandler.class.getName()).log(Level.SEVERE, null, ex);
            }
        }
        return map;
    }

    public Map<String, String> getPostedData(HttpExchange t) {
        try {
            InputStream is = t.getRequestBody();
            BufferedReader bufferedReader = new BufferedReader(new InputStreamReader(is));
            StringBuilder stringBuilder = new StringBuilder();
            String content;
            while ((content = bufferedReader.readLine()) != null) {
                stringBuilder.append(content);
            }
            String uri = stringBuilder.toString();
            return getQueryMap(uri);
        } catch (IOException ex) {
            Logger.getLogger(POSTRequestHandler.class.getName()).log(Level.SEVERE, null, ex);
            return new HashMap<String, String>();
        }
    }

    public abstract PostData getPostData();
}
