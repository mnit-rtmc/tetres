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
package ticas.ticas4.moe;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import ticas.common.config.Config;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.HttpClient;
import ticas.common.period.Period;
import ticas.common.pyticas.responses.ResponseString;
import ticas.common.route.Route;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import ticas.common.infra.Infra;
import ticas.common.util.FileHelper;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class MOEWorker extends Thread {

    public String moeName;
    public String moeURI;
    public List<Period> periods;
    public Route route;
    public String outputPath;
    public boolean hasError = false;
    public String resultMessage;

    public MOEWorker(String moeName, String moeURI, String outputPath, Route route, List<Period> periods) {
        this.moeName = moeName;
        this.moeURI = moeURI;
        this.periods = periods;
        this.route = route;
        this.outputPath = outputPath;
    }

    public String getOutputFilePath() {
        String filepath = outputPath + File.separator + String.format("%s.xlsx", this.moeName);
        return FileHelper.getNumberedFileName(filepath);
    }
    
    @Override
    public void run() {
        PostData pd = new PostData();
        pd.addData("route", this.route);
        pd.addData("periods", this.periods);

        ResponseString res = HttpClient.post_synced(Config.getAPIUrl(this.moeURI), pd, ResponseString.class);
        if(res == null || !res.isSuccess()) {
            resultMessage = String.format("%s - Fail", moeName);
            hasError = true;
                    
        } else {
            byte[] content = Base64.getDecoder().decode(res.obj.getBytes(StandardCharsets.UTF_8));
            String filepath = getOutputFilePath();
            try {            
                FileHelper.writeBinaryFile(content, filepath);
                resultMessage = String.format("%s - Done : %s", moeName, res.obj);
            } catch (IOException ex) {
                resultMessage = String.format("%s - Fail", moeName);
                hasError = true;
            }
            
        }
    }

}
