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

import com.google.gson.reflect.TypeToken;
import ticas.common.config.Config;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.responses.ResponseInteger;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.types.ActionLogInfo;
import java.util.Comparator;
import java.util.Timer;
import javax.swing.JOptionPane;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;

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
        this.URL_LIST = Config.getAPIUrl(ApiURIs.URI.AL_LIST);
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
