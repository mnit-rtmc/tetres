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
package common.pyticas;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class HttpResult {

    public int res_code;
    public String res_msg;
    public String contents;

    public HttpResult(int res_code, String res_msg, String contents) {
        this.res_code = res_code;
        this.res_msg = res_msg;
        this.contents = contents;
    }

    public boolean isSuccess() {
        return this.res_code == 200;
    }

    public boolean isFail() {
        return this.res_code != 200;
    }

    public static HttpResult createErrorResult(String res_msg) {
        return new HttpResult(500, res_msg, "");
    }
}
