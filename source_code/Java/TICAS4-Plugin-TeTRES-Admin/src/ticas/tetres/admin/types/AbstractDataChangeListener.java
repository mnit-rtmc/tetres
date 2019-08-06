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
package ticas.tetres.admin.types;

import ticas.common.pyticas.HttpResult;
import java.util.List;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public abstract class AbstractDataChangeListener<T> {

    public void listSuccess(List<T> list) {
    }

    public void listFailed(HttpResult result) {
    }

    public void getSuccess(T obj) {
    }

    public void getFailed(HttpResult result, int id) {
    }

    public void getFailed(HttpResult result, String name) {
    }

    public void insertSuccess(Integer id) {
    }

    public void insertFailed(HttpResult result, T obj) {
    }

    public void updateSuccess(int id) {
    }

    public void updateFailed(HttpResult result, T obj) {
    }

    public void deleteSuccess(List<Integer> ids) {
    }

    public void deleteFailed(HttpResult result, List<Integer> ids) {
    }

    public void yearsFailed(HttpResult httpResult) {
    }

    public void yearsSuccess(List<Integer> obj) {
    }

    public void insertAllSuccess() {   }
    
    public void insertAllFailed(HttpResult result, List<T> dataList) {   }    
    
}
