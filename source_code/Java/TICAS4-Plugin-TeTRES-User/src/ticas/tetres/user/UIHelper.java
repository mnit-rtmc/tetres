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
package ticas.tetres.user;

import ticas.common.config.Config;
import ticas.tetres.user.types.EstimationRequestInfo;
import ticas.common.util.FileHelper;
import ticas.common.infra.Infra;

import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class UIHelper {
	
	private static EstimationRequestInfo requestInfo;

	public static void saveRequestInfo(EstimationRequestInfo eri) {
		requestInfo = eri;
	}

	public static EstimationRequestInfo getPreviousRequestInfo() {
		return requestInfo;
	}

	public static void importRequestInfo() {
		String riJSON = Config.getDownloadedRequestInfo();
		requestInfo = EstimationRequestInfo.fromJSON(riJSON);
	}

	private static String configDirPath() {
		String dataPath = Infra.getInstance().getDataPath();
		String filterDirPath = dataPath + File.separator + "tetres";
		if (!FileHelper.exists(filterDirPath)) {
			FileHelper.createDirs(filterDirPath);
		}
		return filterDirPath;
	}

	public static void setTimeout(Runnable runnable, int delay){
		new Thread(() -> {
			try {
				Thread.sleep(delay);
				runnable.run();
			}
			catch (Exception e){
				System.err.println(e);
			}
		}).start();
	}
}
