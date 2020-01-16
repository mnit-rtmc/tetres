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
package user.api;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.config.Config;
import common.log.TICASLogger;
import common.pyticas.PostData;
import common.pyticas.HttpClient;
import common.pyticas.responses.Response;
import user.TeTRESConfig;
import user.types.EstimationRequestInfo;
import user.types.IResultIsReady;
import user.types.Protocol;
import user.types.ResponseEstimation;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.MalformedURLException;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.List;
import javax.swing.JOptionPane;
import net.lingala.zip4j.core.ZipFile;
import net.lingala.zip4j.exception.ZipException;
import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.core.Logger;
import common.pyticas.IRequest;
import common.pyticas.RunningDialog;
import common.util.FileHelper;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class EstimationAPIClient {

    private final Integer RESULT_CHECK_INTERVAL = 15 * 1000; // 15 seconds

    protected Gson gsonBuilder = new GsonBuilder().create();
    protected Logger logger;

    public EstimationAPIClient() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
    }

    public void estimate(List<Integer> routeIDs, EstimationRequestInfo estRequest, IResultIsReady callback) {
        // faverolles 10/7/2019:
        //  Send selected parameters (EstimationRequestInfo estRequest) to python server

        String uid = null;
        PostData pd = new PostData();
        pd.addData("routeIDs", routeIDs);
        pd.addData("param", estRequest);
        ResponseEstimation response = HttpClient.post_synced(Config.getAPIUrl(ApiURIs.URI.ESTIMATION), pd, ResponseEstimation.class);
        if(response == null) {
            this.logger.info("Fail to estimate (reason=HTTP ERROR)");
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to estimation (HTTP ERROR)");            
            return;
        }
        if (response.code == Protocol.SUCCESS) {
            uid = response.obj.uid;
        } else {
            this.logger.info("Fail to estimate (reason=" + response.message + ")");
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, response.message);
            return;
        }
        
        final String paramUid = uid;

        RunningDialog.run(new IRequest() {
            
            @Override
            public void request() {
                
                String resultCheckingURL = Config.getAPIUrl(ApiURIs.URI.ESTIMATION_RESULT);
                PostData pd = new PostData();
                pd.addData("uid", paramUid);

                while (true) {
                    logger.info("Checking if result is ready... (" + resultCheckingURL + ")");
                    Response response = HttpClient.post_synced(resultCheckingURL, pd, Response.class);
                    if (response == null) {
                        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Disconnected from TeTRES Server");
                        return;
                    }
                    if (response.isSuccess()) {
                        download(paramUid, callback);
                        break;
                    }

                    try {
                        Thread.sleep(RESULT_CHECK_INTERVAL);
                    } catch (InterruptedException ex) {
                        logger.info(ex);
                    }

                }
            }
        });
 
    }

    private void unzip(String fileZip, String destinationDirectory, boolean deleteZipFile) {
        this.logger.info("Unzipping... (" + fileZip + ")");
        try {
            ZipFile zipFile = new ZipFile(fileZip);
            zipFile.extractAll(destinationDirectory);
            if (deleteZipFile) {
                Files.delete((new File(fileZip)).toPath());
            }
        } catch (ZipException ex) {
            this.logger.info(ex);
        } catch (IOException ex) {
            this.logger.info(ex);
        }
    }

    public void download(String uid, IResultIsReady callback) {
        String downloadURL = Config.getAPIUrl(ApiURIs.URI.ESTIMATION_DOWNLOAD) + "?uid=" + uid;
        this.logger.info("Downloading... (" + downloadURL + ")");
        String resultFolder = this.outputPath(null);
        String zipFile = this.outputPath(uid + ".zip");
        if (zipFile == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Cannot find the output directory");
            callback.OnReady(null, null);
            return;
        }
        try {
            URL downloadZipUrl = new URL(downloadURL);
            Path targetPath = (new File(zipFile)).toPath();
            try (InputStream in = downloadZipUrl.openStream()) {
                Files.copy(in, targetPath, StandardCopyOption.REPLACE_EXISTING);
                if(FileHelper.exists(zipFile)) {
                    unzip(zipFile, resultFolder, true);
                    callback.OnReady(uid, this.outputPath(uid));
                } else {
                    callback.OnReady(null, null);
                }
            } catch (IOException ex) {
                this.logger.info(ex);
                callback.OnReady(null, null);
            }
        } catch (MalformedURLException ex) {
            this.logger.info(ex);
            callback.OnReady(null, null);
        }
    }

    public String outputPath(String name) {
        String resultPath = TeTRESConfig.getDataPath(TeTRESConfig.RESULT_DIR_NAME, true);
        if (resultPath == null) {
            return null;
        }
        if (name != null) {
            return resultPath + File.separator + name;
        } else {
            return resultPath;
        }
    }
}
