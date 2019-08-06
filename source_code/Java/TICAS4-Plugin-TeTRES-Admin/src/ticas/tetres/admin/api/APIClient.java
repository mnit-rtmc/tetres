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
package ticas.tetres.admin.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.responses.Response;
import ticas.common.pyticas.responses.ResponseInteger;
import ticas.common.pyticas.responses.ResponseIntegerList;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.tetres.admin.types.InfoBase;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Timer;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.Logger;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 * @param <T>
 */
public abstract class APIClient<T extends InfoBase> {

    protected String URL_DELETE;
    protected String URL_LIST;
    protected String URL_LIST_BY_YEAR;
    protected String URL_INSERT;
    protected String URL_INSERT_ALL;
    protected String URL_UPDATE;
    protected String URL_GET;
    protected String URL_YEARS;
    protected Type RESPONSE_LIST_TYPE;
    protected Type RESPONSE_TYPE;
    protected Type DATA_TYPE;
    protected Gson gsonBuilder = new GsonBuilder().create();
    public final ArrayList<T> dataList;
    protected List<AbstractDataChangeListener<T>> changeListeners = new ArrayList<>();
    protected boolean isLoadingList = false;
    protected Logger logger;
    private Integer dialogOpenDelay = 20;

    public APIClient() {
        dataList = new ArrayList<T>();
        logger = TICASLogger.getLogger(this.getClass().getName());
    }

    public void yearsWithoutProgress() {
        HttpClient.get(this.URL_YEARS, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                try {
                    Gson gsonBuilder = new GsonBuilder().create();
                    ResponseIntegerList obj = gsonBuilder.fromJson(res.contents, ResponseIntegerList.class);
                    obj.httpResult = res;
                    fireYearsSuccess(obj.obj);
                } catch (Exception ex) {
                    ex.printStackTrace();
                    fireYearsFailed(res);
                }
            }

            @Override
            public void fail(HttpResult res) {
                fireYearsFailed(res);
            }
        });
    }

    public void years() {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.get_synced(URL_YEARS);
                if (res.isSuccess()) {
                    try {
                        Gson gsonBuilder = new GsonBuilder().create();
                        ResponseIntegerList obj = gsonBuilder.fromJson(res.contents, ResponseIntegerList.class);
                        obj.httpResult = res;
                        fireYearsSuccess(obj.obj);
                    } catch (Exception ex) {
                        ex.printStackTrace();
                        fireYearsFailed(res);
                    }
                } else {
                    fireYearsFailed(res);
                }
            }
        });
    }

    public void list() {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.get_synced(URL_LIST);
                IHttpResultCallback callback = getListCallback();
                if (res.isSuccess()) {
                    callback.ready(res);
                } else {
                    callback.fail(res);
                }
            }
        });
    }

    public void listByYear(Integer year) {

        final PostData pd = new PostData();
        if (year != null) {
            pd.addData("year", year);
        }

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.post_synced(URL_LIST_BY_YEAR, pd);
                IHttpResultCallback callback = getListCallback();
                if (res.isSuccess()) {
                    callback.ready(res);
                } else {
                    callback.fail(res);
                }
            }
        });
    }

    private T getDataById(int id) {
        for (T obj : this.dataList) {
            if (obj.id == id) {
                return obj;
            }
        }
        return null;
    }

    public void delete(final List<Integer> ids) {
        Integer[] idsArray = ids.toArray(new Integer[ids.size()]);
        final PostData pd = new PostData();
        pd.addData("ids", idsArray);

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult result = HttpClient.post_synced(URL_DELETE, pd);
                if (result.isSuccess()) {
                    ResponseIntegerList response = gsonBuilder.fromJson(result.contents, ResponseIntegerList.class);
                    if (!response.isSuccess()) {
                        fireDeleteFailed(result, ids);
                        return;
                    }
                    for (Integer deletedId : response.obj) {
                        T obj = getDataById(deletedId);
                        if (obj != null) {
                            dataList.remove(obj);
                        }
                    }
                    fireDeleteSuccess(response.obj);
                } else {
                    fireDeleteFailed(result, ids);
                }
            }
        });
    }

    public void insert(final T obj) {
        final PostData pd = new PostData();
        pd.addData("data", toJson(obj));

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult result = HttpClient.post_synced(URL_INSERT, pd);
                if (result.isSuccess()) {
                    ResponseInteger resp = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    if (resp.isSuccess()) {
                        fireInsertSuccess(resp.obj);
                    } else {
                        fireInsertFailed(result, obj);
                    }
                } else {
                    fireInsertFailed(result, obj);
                }
            }
        });
    }

    public void insertAll(final List<T> dataList) {

        List<String> strList = new ArrayList<>();
        for (T obj : dataList) {
            strList.add(toJson(obj));
        }

        final PostData pd = new PostData();
        pd.addData("data", toJson(strList));

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult result = HttpClient.post_synced(URL_INSERT_ALL, pd);
                if (result.isSuccess()) {
                    Response resp = gsonBuilder.fromJson(result.contents, Response.class);
                    if (resp.isSuccess()) {
                        fireInsertAllSuccess();
                    } else {
                        fireInsertAllFailed(result, dataList);
                    }
                } else {
                    fireInsertAllFailed(result, dataList);
                }
            }
        });
    }

    public void get(final String id) {
        PostData pd = new PostData();
        pd.addData("id", id);

        HttpClient.post(this.URL_GET, pd, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                if (result.isSuccess()) {
                    ObjectResponse<T> resp = gsonBuilder.fromJson(result.contents, RESPONSE_TYPE);
                    fireGetSuccess(resp.obj);
                } else {
                    fireGetFailed(result, id);
                }
            }

            @Override
            public void fail(HttpResult result) {
                fireGetFailed(result, id);
            }
        });
    }

    public T getSynced(String id) {
        PostData pd = new PostData();
        pd.addData("id", id);
        HttpResult res = HttpClient.post_synced(this.URL_GET, pd);
        if (res.isSuccess()) {
            ObjectResponse<T> resp = gsonBuilder.fromJson(res.contents, this.RESPONSE_TYPE);
            if (resp.isSuccess()) {
                fireGetSuccess(resp.obj);
                return resp.obj;
            } else {
                fireGetFailed(res, id);
                return null;
            }
        } else {
            fireGetFailed(res, id);
            return null;
        }
    }

    public T getByNameSynced(final String name) {
        PostData pd = new PostData();
        pd.addData("name", name);
        HttpResult res = HttpClient.post_synced(this.URL_GET, pd);
        if (res.isSuccess()) {
            ObjectResponse<T> resp = gsonBuilder.fromJson(res.contents, RESPONSE_TYPE);
            if (resp.isSuccess()) {
                fireGetSuccess(resp.obj);
                return resp.obj;
            } else {
                fireGetFailed(res, name);
                return null;
            }
        } else {
            fireGetFailed(res, name);
            return null;
        }
    }

    public void update(T exData, final T newData) {
        final PostData pd = new PostData();
        pd.addData("id", exData.id);
        pd.addData("data", newData);

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult result = HttpClient.post_synced(URL_UPDATE, pd);
                if (result.isSuccess()) {
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);
                    if (response.isSuccess()) {
                        fireUpdateSuccess(response.obj);
                    } else {
                        fireUpdateFailed(result, newData);
                    }
                } else {
                    fireUpdateFailed(result, newData);
                }
            }
        });
    }

    protected IHttpResultCallback getListCallback() {
        return new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                if (res.isSuccess()) {
                    isLoadingList = false;
                    try {
                        ListResponse<T> obj = gsonBuilder.fromJson(res.contents, RESPONSE_LIST_TYPE);
                        if (obj.isSuccess()) {
                            dataList.clear();
                            for (T sne : obj.obj.list) {
                                dataList.add(sne);
                            }
                            Collections.sort(dataList, getComparator());
                            fireListSuccess();
                        } else {
                            fireListFailed(res);
                        }
                    } catch (Exception ex) {
                        ex.printStackTrace();
                        fireListFailed(res);
                    }
                } else {
                    fireListFailed(res);
                }
            }

            @Override
            public void fail(HttpResult res) {
                isLoadingList = false;
                fireListFailed(res);
            }
        };
    }

    protected void notSupportedAPI(String name) {
        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Not Supported API : " + name);
    }

    public String toJson(Object obj) {
        return gsonBuilder.toJson(obj);
    }

    protected abstract Comparator<T> getComparator();

    public void addChangeListener(AbstractDataChangeListener<T> listener) {
        changeListeners.add(listener);
    }

    public void removeChangeListener(AbstractDataChangeListener<T> listener) {
        changeListeners.remove(listener);
    }

    protected void fireListSuccess() {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.listSuccess(dataList);
        }
    }

    protected void fireListFailed(HttpResult httpResult) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.listFailed(httpResult);
        }
    }

    protected void fireGetSuccess(T obj) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.getSuccess(obj);
        }
    }

    protected void fireGetFailed(HttpResult httpResult, int id) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.getFailed(httpResult, id);
        }
    }

    protected void fireGetFailed(HttpResult httpResult, String id) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.getFailed(httpResult, id);
        }
    }

    protected void fireUpdateSuccess(int id) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.updateSuccess(id);
        }
    }

    protected void fireUpdateFailed(HttpResult httpResult, T obj) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.updateFailed(httpResult, obj);
        }
    }

    protected void fireDeleteSuccess(List<Integer> ids) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.deleteSuccess(ids);
        }
    }

    protected void fireDeleteFailed(HttpResult httpResult, List<Integer> ids) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.deleteFailed(httpResult, ids);
        }
    }

    protected void fireInsertSuccess(Integer insertedId) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.insertSuccess(insertedId);
        }
    }

    protected void fireInsertFailed(HttpResult httpResult, T obj) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.insertFailed(httpResult, obj);
        }
    }

    private void fireYearsSuccess(List<Integer> obj) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.yearsSuccess(obj);
        }
    }

    private void fireYearsFailed(HttpResult httpResult) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.yearsFailed(httpResult);
        }
    }

    private void fireInsertAllSuccess() {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.insertAllSuccess();
        }
    }

    private void fireInsertAllFailed(HttpResult result, List<T> dataList) {
        for (AbstractDataChangeListener<T> listener : changeListeners) {
            listener.insertAllFailed(result, dataList);
        }
    }
}
