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
package admin.api;

import com.google.gson.reflect.TypeToken;
import common.config.Config;
import common.log.TICASLogger;
import common.pyticas.HttpClient;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import common.pyticas.responses.ResponseInteger;
import admin.TeTRESConfig;
import admin.api.APIClient;
import admin.api.ApiURIs;
import admin.api.ListResponse;
import admin.api.ObjectResponse;
import admin.types.ActionLogInfo;
import java.util.Comparator;
import java.util.Timer;
import javax.swing.JOptionPane;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class ActionLogClient extends APIClient<ActionLogInfo> {

    private final String URL_PROCEED;

    public ActionLogClient() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.RESPONSE_LIST_TYPE = new TypeToken<ListResponse<ActionLogInfo>>(){}.getType();
        this.RESPONSE_TYPE = new TypeToken<ObjectResponse<ActionLogInfo>>(){}.getType();
        this.DATA_TYPE = ActionLogInfo.class;                
        this.URL_LIST = Config.getAPIUrl(admin.api.ApiURIs.URI.AL_LIST);
        this.URL_PROCEED = Config.getAPIUrl(ApiURIs.URI.AL_PROCEED);
    }

    public void list(Integer limit) {
        if (isLoadingList) {
            return;
        }
        
        isLoadingList = true;
        final PostData pd = new PostData();
        pd.addData("limit", limit);        
        HttpClient.post(this.URL_LIST, pd, getListCallback());
        
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.post_synced(URL_LIST, pd);
                IHttpResultCallback callback = getListCallback();                
                if (res.isSuccess()) {
                    callback.ready(res);
                } else {
                    callback.fail(res);
                }
            }
        });
    }
    
    
    public void proceed() {
        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                HttpResult res = HttpClient.get_synced(URL_PROCEED);
                if (res.isSuccess()) {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Success\nThe process is started in background");
                } else {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to request");                    
                }
            }
        });
    }    
    
    @Override
    protected Comparator<ActionLogInfo> getComparator() {
        return new Comparator<ActionLogInfo>() {
            @Override
            public int compare(ActionLogInfo o1, ActionLogInfo o2) {
                return o2.reg_date.compareTo(o1.reg_date);
            }
        };
    }    
}
