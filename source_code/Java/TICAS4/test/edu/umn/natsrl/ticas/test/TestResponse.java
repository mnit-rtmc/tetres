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
package edu.umn.natsrl.ticas.test;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.common.route.Route;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.Map;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TestResponse {

    public static void main(String[] args) throws IOException, InterruptedException {
        String json_str = "{\"message\": \"Test\", \"code\": 1, \"obj\": {\"name\": \"Route I-35W NB\", \"rnodes\": [\"rnd_86379\", \"rnd_86383\", \"rnd_86381\", \"rnd_86385\", \"rnd_95771\", \"rnd_86389\", \"rnd_86391\"], \"cfg\": null, \"desc\": \"Route created at 2016-02-23 13:15:32 \", \"__module__\": \"pyticas.types\", \"__class__\": \"Route\", \"infra_cfg_date\": \"2015-09-08\"}}";

        Gson gsonBuilder = new GsonBuilder().create();
//        Type resType = new TypeToken<Response<Route>>() {}.getType();
//        Response<Route> res = gsonBuilder.fromJson(json_str, resType);
//        System.out.println("Res1:" + res.code + " > " + res.message);
//        System.out.println("Route1:" + res.obj.name);
    }
//        
//        Response<Route> res2 = TestResponse.by_func(json_str, Route.class);
//        System.out.println("Res2:" + res2.code + " > " + res2.message);
//        System.out.println("Route2:" + res2.obj.name);
        
//        Response<Route> res3 = TestResponse.by_func2(json_str, Route.class);
//        System.out.println("Res3:" + res3.code + " > " + res3.message);
//        System.out.println("Route3:" + res3.obj.name);
//        
//        Response<Route> res4 = TestResponse.by_func(json_str, Route.class);
//        System.out.println("Res4:" + res4.code + " > " + res4.message);
//        System.out.println("Route4:" + res4.obj.name);


//    }

//    public static <T> Response<T> by_func(String json_str, Class<T> type) throws FileNotFoundException, IOException {
//        Gson gsonBuilder = new GsonBuilder().create();
//        Type resType = new TypeToken<Response<T>>() {
//        }.getType();        
//        Response<T> res = gsonBuilder.fromJson(json_str, resType);
//        return res;
//    }
//
//    public static <T> Response<T> by_func(String json_str, Class<T> type) throws FileNotFoundException, IOException {
//        Type resType = new TypeToken<Response<T>>() {
//        }.getType();
//        return TestResponse.by_func(json_str, resType);
//    }
//
//    private static <T> Response<T> by_func(String json_str, Type resType) {
//        Gson gsonBuilder = new GsonBuilder().create();
//        Response<T> res = gsonBuilder.fromJson(json_str, resType);
//        return res;
//    }
}
