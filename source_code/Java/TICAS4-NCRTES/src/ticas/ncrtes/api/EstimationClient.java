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
package ticas.ncrtes.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.config.Config;
import ticas.common.infra.Infra;
import ticas.common.log.TICASLogger;
import ticas.ncrtes.NCRTESConfig;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.ncrtes.types.EstimationRequestInfo;
import ticas.common.util.FileHelper;
import java.util.Timer;
import java.util.TimerTask;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.Logger;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class EstimationClient {

    protected Logger logger;

    public EstimationClient() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
    }

    public void estimate(EstimationRequestInfo estRequest) {

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                PostData pd = new PostData();
                pd.addData("param", estRequest);
                HttpClient.post(Config.getAPIUrl(ApiURIs.URI.ESTIMATION), pd, new IHttpResultCallback() {
                    @Override
                    public void ready(HttpResult result) {
                        FileHelper.openDirectory(outputPath(null));
                        JOptionPane.showMessageDialog(Config.mainFrame, "Done");
                        logger.info("Estimation Success");
                    }

                    @Override
                    public void fail(HttpResult result) {
                        JOptionPane.showMessageDialog(Config.mainFrame, "Fail");
                        logger.info("Estimation Failed");
                    }
                });
            }
        });
    }

    private String outputPath(String resultDir) {
        String dataPath = Infra.getInstance().getDataPath();
        if (resultDir == null) {
            return FileHelper.absolutePath(dataPath + "/" + NCRTESConfig.resultDir);
        } else {
            return FileHelper.absolutePath(dataPath + "/" + NCRTESConfig.resultDir + "/" + resultDir);
        }
    }
}
