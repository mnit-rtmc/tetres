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
package ncrtes.api;

import common.config.Config;
import common.log.TICASLogger;
import common.pyticas.HttpResult;
import common.pyticas.IHttpResultCallback;
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.Logger;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TSIClient {

    protected Logger logger;

    public TSIClient() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
    }

    public void requestRun(String year) {

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                PostData pd = new PostData();
                pd.addData("year", year);
                HttpClient.post(Config.getAPIUrl(ApiURIs.URI.TSI), pd, new IHttpResultCallback() {
                    @Override
                    public void ready(HttpResult result) {
                        JOptionPane.showMessageDialog(null, "Done");
                        logger.info("TSI Success");
                    }

                    @Override
                    public void fail(HttpResult result) {
                        JOptionPane.showMessageDialog(null, "Fail");
                        logger.info("TSI Failed");
                    }
                });
            }
        }, "Please wait... It may take several hours");
    }

}
