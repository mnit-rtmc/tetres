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

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.log.TICASLogger;
import common.pyticas.responses.Response;

import java.io.*;
import java.lang.reflect.Type;
import java.net.*;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class HttpClient {

    private static String USER_AGENT = "TICAS4 Client";

    public static HttpURLConnection getConnection(String target_url)
            throws FileNotFoundException, IOException, NoSuchAlgorithmException, KeyManagementException {
        URL url = new URL(target_url);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        CookieManager cookieManager = new CookieManager();
        CookieHandler.setDefault(new CookieManager(null, CookiePolicy.ACCEPT_ALL));
        conn.setRequestProperty("User-Agent", USER_AGENT);
        return conn;
    }

    public static HttpResult get_synced(String target_url) {
        org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(HttpClient.class.getName());
        try {
            logger.info(String.format("HTTP Request [GET]: %s", target_url));
            StringBuilder result = new StringBuilder();
            HttpURLConnection conn = getConnection(target_url);
            conn.setRequestMethod("GET");
            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;

            int responseCode = conn.getResponseCode();
            String responseMessage = conn.getResponseMessage();

            logger.debug(String.format("Response Code : %d", responseCode));
            logger.debug(String.format("Response Message : %s", responseMessage));

            while ((line = rd.readLine()) != null) {
//                logger.debug(String.format("Read Line : %s", line));
                result.append(line);
            }
            //logger.debug("Response Body: " + result.toString());
            rd.close();
            return new HttpResult(responseCode, responseMessage, result.toString());

        } catch (IOException ex) {
            ex.printStackTrace();
            logger.warn("Exception occured in HTTP [GET] : " + target_url);
            logger.debug("Exception occured in HTTP [GET] : " + target_url, ex);
            return HttpResult.createErrorResult("Exception Occured : " + ex.toString());
        } catch (NoSuchAlgorithmException ex) {
            ex.printStackTrace();
            logger.warn("NoSuchAlgorithmException occured in HTTP [GET] : " + target_url);
            logger.debug("NoSuchAlgorithmException occured in HTTP [GET] : " + target_url, ex);
            return HttpResult.createErrorResult("Exception Occured : " + ex.toString());
        } catch (KeyManagementException ex) {
            ex.printStackTrace();
            logger.warn("KeyManagementException occured in HTTP [GET] : " + target_url);
            logger.debug("KeyManagementException occured in HTTP [GET] : " + target_url, ex);
            return HttpResult.createErrorResult("Exception Occured : " + ex.toString());
        }
    }

    public static <T extends Response> T get_synced(String target_url, final Class<T> type) {

        HttpResult res = get_synced(target_url);

        if (res.isSuccess()) {
            Gson gsonBuilder = new GsonBuilder().create();
            T obj = gsonBuilder.fromJson(res.contents, type);
            obj.httpResult = res;
            return obj;
        } else {
            TICASLogger.getLogger(HttpClient.class.getName())
                       .error(String.format("Fail to HTTP GET : URL= %s", target_url));
            return null;
        }
    }

    public static HttpResult post_synced(String target_url, PostData postData) {
        org.apache.logging.log4j.core.Logger logger = TICASLogger.getLogger(HttpClient.class.getName());
        try {
            String data = postData.getPostDataString();
            logger.info(String.format("HTTP Request [POST]: %s", target_url));
            logger.debug(String.format("PostData : %s", data));
            StringBuilder result = new StringBuilder();
            HttpURLConnection conn = getConnection(target_url);
            conn.setConnectTimeout(60 * 60 * 1000);
            conn.setReadTimeout(7 * 60 * 60 * 1000);
            conn.setRequestMethod("POST");
            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Length", Integer.toString(data.length()));
            DataOutputStream wr = new DataOutputStream(conn.getOutputStream());
            wr.writeBytes(data);
            wr.flush();
            wr.close();

            int responseCode = conn.getResponseCode();
            String responseMessage = conn.getResponseMessage();
            logger.debug(String.format("Response Code : %d", responseCode));
            logger.debug(String.format("Response Message : %s", responseMessage));

            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            while ((line = rd.readLine()) != null) {
//                logger.debug(String.format("Read Line : %s", line));
                result.append(line);
            }
            //logger.debug("Response Body: " + result.toString());
            rd.close();
            return new HttpResult(responseCode, responseMessage, result.toString());
        } catch (UnsupportedEncodingException ex) {
            ex.printStackTrace();
            logger.warn(String.format("UnsupportedEncodingException: %s", ex.toString()));
            logger.debug(String.format("UnsupportedEncodingException: %s", ex.toString(), ex));
            return HttpResult.createErrorResult("UnsupportedEncodingException Occured : " + ex.toString());
        } catch (IOException ex) {
            ex.printStackTrace();
            logger.warn(String.format("IOException: %s", ex.toString()));
            logger.debug(String.format("IOException: %s", ex.toString()), ex);
            return HttpResult.createErrorResult("IOException Occured : " + ex.toString());
        } catch (NoSuchAlgorithmException ex) {
            ex.printStackTrace();
            logger.warn(String.format("NoSuchAlgorithmException: %s", ex.toString()));
            logger.debug(String.format("NoSuchAlgorithmException: %s", ex.toString()), ex);
            return HttpResult.createErrorResult("NoSuchAlgorithmException Occured : " + ex.toString());
        } catch (KeyManagementException ex) {
            ex.printStackTrace();
            logger.warn(String.format("KeyManagementException: %s", ex.toString()));
            logger.debug(String.format("KeyManagementException: %s", ex.toString()), ex);
            return HttpResult.createErrorResult("KeyManagementException Occured : " + ex.toString());
        }
    }

    public static <T extends Response> T post_synced(String target_url, PostData pd, final Class<T> type) {
        HttpResult res = post_synced(target_url, pd);
        if (res.isSuccess()) {
            Gson gsonBuilder = new GsonBuilder().create();
            T obj = gsonBuilder.fromJson(res.contents, type);
            obj.httpResult = res;
            return obj;
        } else {
            TICASLogger.getLogger(HttpClient.class.getName())
                       .warn(String.format("Fail to HTTP POST : URL= %s", target_url));
            return null;
        }
    }

    public static <T extends Response> T post_synced(String target_url, PostData pd, Type type) {
        HttpResult res = post_synced(target_url, pd);
        if (res.isSuccess()) {
            Gson gsonBuilder = new GsonBuilder().create();
            T obj = gsonBuilder.fromJson(res.contents, type);
            obj.httpResult = res;
            return obj;
        } else {
            TICASLogger.getLogger(HttpClient.class.getName())
                       .warn(String.format("Fail to HTTP POST : URL= %s", target_url));
            return null;
        }
    }

    public static void get(String target_url, IHttpResultCallback callback) {
        RestClientWorker wt = new RestClientWorker(target_url, callback);
        wt.start();
    }

    public static <T extends Response> void get(String target_url, final IResponseCallback<T> callback,
            final Class<T> type) {
        HttpClient.get(target_url, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                if (res.isSuccess()) {
                    try {
                        Gson gsonBuilder = new GsonBuilder().create();
                        T obj = gsonBuilder.fromJson(res.contents, type);
                        obj.httpResult = res;
                        if (callback != null) {
                            callback.success(obj);
                        }
                    } catch (Exception ex) {
                        ex.printStackTrace();
                        System.out.println(res.contents);
                        callback.fail(res);
                    }
                } else if (callback != null) {
                    callback.fail(res);
                }
            }

            @Override
            public void fail(HttpResult result) {
                if (callback != null) {
                    callback.fail(result);
                }
            }
        });
    }

    public static void post(String uri_path, PostData pd, IHttpResultCallback callback) {
        RestClientWorker wt = new RestClientWorker(uri_path, pd, callback);
        wt.start();
    }

    public static <T extends Response> void post(String uri_path, PostData pd, final IResponseCallback<T> callback,
            final Class<T> type) {
        HttpClient.post(uri_path, pd, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                if (res.isSuccess()) {
                    Gson gsonBuilder = new GsonBuilder().create();
                    T obj = gsonBuilder.fromJson(res.contents, type);
                    obj.httpResult = res;
                    if (callback != null) {
                        callback.success(obj);
                    }
                } else if (callback != null) {
                    callback.fail(res);
                }
            }

            @Override
            public void fail(HttpResult result) {
                if (callback != null) {
                    callback.fail(result);
                }
            }
        });
    }
}
