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
package ticas.common.pyticas.responses;

import ticas.common.pyticas.HttpResult;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Response {   
    public Integer code;
    public String message;
    public HttpResult httpResult;
    
    public boolean isSuccess() {
        return this.code == 1;
    }
}

