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

import ticas.common.config.Config;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.HttpClient;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TestRest {

    public static void main(String[] args) {

        HttpClient.get(Config.getAPIUrl("/ticas/infra"), new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                System.out.println(result.contents);
            }

            @Override
            public void fail(HttpResult res) {
                System.out.println("Fail to load infra information");
            }
        });

    }

}
