package ticas.ncrtes.estimation.test;

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
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.log.TICASLogger;
import ticas.ncrtes.types.BarealaneRegainTimeInfo;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.lang.reflect.Type;
import java.net.HttpURLConnection;
import java.net.URL;
import ticas.common.pyticas.PostData;
import ticas.ncrtes.types.EstimationRequestInfo;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import java.io.Reader;
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TestEstimation {

    public static void main(String args[]) {
        EstimationRequestInfo er = new EstimationRequestInfo("pyticas_ncrtes.ncrtes_types", "EstimationRequestInfo");
        er.snow_start_time = "2012-01-20 06:00:00";
        er.snow_end_time = "2012-01-20 16:30:00";
        er.target_corridors.add("I-35E (NB)");
        Gson gsonBuilder = new GsonBuilder().create();
        String json_data = gsonBuilder.toJson(er);
        PostData pd = new PostData();
        pd.addData("param", json_data);
        TestEstimation.post_synced("http://localhost:5000/ncrtes/est/", pd, new IHttpCallback() {
            @Override
            public void gotPushMessage(String msg) {
                System.out.println("Get Message : " + msg);
            }
        });
    }

    public static void post(String uri_path, PostData pd, IHttpCallback callback) {
        TestRestClientWorker wt = new TestRestClientWorker(uri_path, pd, callback);
        wt.start();
    }

    private static String USER_AGENT = "TICAS4 Client";

    public static HttpURLConnection getConnection(String target_url) throws FileNotFoundException, IOException {
        URL url = new URL(target_url);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestProperty("User-Agent", USER_AGENT);
        return conn;
    }

    public static void post_synced(String target_url, PostData postData, IHttpCallback callback) {
        try {
            String data = postData.getPostDataString();
            System.out.println(String.format("HTTP Request [POST]: %s", target_url));
            System.out.println(String.format("PostData : %s", data));
            StringBuilder result = new StringBuilder();
            HttpURLConnection conn = getConnection(target_url);
            conn.setReadTimeout(60 * 60 * 1000);
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
            System.out.println(String.format("Response Code : %d", responseCode));
            System.out.println(String.format("Response Message : %s", responseMessage));

            InputStreamReader is = new InputStreamReader(conn.getInputStream());
            char[] buffer = new char[1024];
            while (is.read(buffer, 0, 1024) != -1) {
                String msg = new String(buffer);
                String[] msgs = msg.split("\n");
                for(int i=0; i<msgs.length; i++) {
                    if(msgs[i].trim().isEmpty()) continue;
                    System.out.println(String.format("Read Line : %s", msgs[i].trim()));                    
                }
            }             
            is.close();
            
        } catch (UnsupportedEncodingException ex) {
            System.out.println(String.format("UnsupportedEncodingException: %s", ex.toString()));
        } catch (IOException ex) {
            System.out.println(String.format("IOException: %s", ex.toString()));
        }
    }
}
