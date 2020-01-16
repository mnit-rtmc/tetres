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

import common.config.Config;
import common.log.TICASLogger;
import java.io.*;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class PyTICASServer extends Thread {

    public boolean isStarted = false;
    public boolean useExe = false;

    public PyTICASServer() {
    }

    @Override
    public void run() {
        HttpClient.get(Config.getAPIUrl("/ticas/ison"), new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                if (result == null || result.res_code != 200) {
                    if (!useExe) {
                        executeServerScript();
                    } else {                        
                        executeServerExe();
                    }
                } else {
                    TICASLogger.getLogger(PyTICASServer.class.getName()).info("PyTICAS server is aready running");
                }
            }

            @Override
            public void fail(HttpResult result) {
                if (!useExe) {
                    executeServerScript();
                } else {
                    executeServerExe();
                }
                //TICASLogger.getLogger(PyTICASServer.class.getName()).info("could not check if PyTICAS server is running (1)");
            }
        });
    }

    public void executeServerScript() {
        final Logger logger = TICASLogger.getLogger(PyTICASServer.class.getName());
        logger.info("server script : " + Config.getServerPath());
        try {
            ProcessBuilder pb = new ProcessBuilder(Config.getPythonPath(), Config.getServerPath(), "-p", Config.getServerPort());
            Process p = pb.start();
            BufferedReader in = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            isStarted = true;
            logger.info("PyTICAS Local Server has been started");
            while (true) {
                String line = in.readLine();
                if (line != null) {
                    System.err.println(line);
                }
            }
        } catch (IOException ex) {
            logger.info("could not run the PyTICAS Server");
        }
    }

    public void executeServerExe() {
        final Logger logger = TICASLogger.getLogger(PyTICASServer.class.getName());
        logger.info("Try to run server.exe");
        try {
            ProcessBuilder pb = new ProcessBuilder("server.exe", "-p", Config.getServerPort());
            Process p = pb.start();
            BufferedReader in = new BufferedReader(new InputStreamReader(p.getErrorStream()));
            isStarted = true;
            logger.info("PyTICAS Local Server has been started");
            try {
                while (true) {
                    String line = in.readLine();
                    if (line != null) {
                        System.err.println(line);
                    }
                }
            } catch(Exception ex) {
                logger.info("PyTICAS Local Server : exception occured");                
            }
        } catch (IOException ex) {
            logger.info("could not run the PyTICAS Server");
        }
    }

    public int stopServerSynced() {
        final Logger logger = TICASLogger.getLogger(PyTICASServer.class.getName());
        HttpResult res = HttpClient.get_synced(Config.getAPIUrl("/ticas/turnoff"));
        return res.res_code;
    }

    public void stopServer() {
        final Logger logger = TICASLogger.getLogger(PyTICASServer.class.getName());
        HttpClient.get(Config.getAPIUrl("/ticas/turnoff"), new IHttpResultCallback() {

            @Override
            public void ready(HttpResult result) {
                logger.info("local PyTICAS Server has been terminated");
            }

            @Override
            public void fail(HttpResult result) {
                logger.info("could not stop local PyTICAS Server");
            }
        });
    }
//    @Override
//    public void finalize() throws Throwable {
//        this.stopServer();
//        super.finalize();
//    }
}
