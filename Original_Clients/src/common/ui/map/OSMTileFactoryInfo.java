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
package common.ui.map;

import common.infra.Infra;
import common.log.TICASLogger;
import common.util.FileHelper;
import java.io.BufferedInputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URL;
import java.net.URLConnection;
import org.apache.logging.log4j.core.Logger;
import org.jdesktop.swingx.mapviewer.TileFactoryInfo;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class OSMTileFactoryInfo extends TileFactoryInfo {

	private final int mapZoom;
	private final String name;
	private final Infra infra;
	private final Logger logger;

	public OSMTileFactoryInfo(String name, String baseURL, int minimumZoomLevel, int maximumZoomLevel, int totalMapZoom,
			int tileSize, boolean xr2l, boolean yt2b) {
		super(minimumZoomLevel, maximumZoomLevel, totalMapZoom, tileSize, xr2l, yt2b, null, null, null, null);
		this.name = name;
		this.mapZoom = totalMapZoom;
		this.baseURL = baseURL;
		this.infra = Infra.getInstance();
		this.logger = TICASLogger.getLogger(this.getClass().getName());
	}

	@Override
	public String getTileUrl(int x, int y, int zoom) {

		int z = this.mapZoom - zoom;

		String url = baseURL
				+ "/" + z
				+ "/" + x
				+ "/" + y
				+ ".png";

		//System.out.println(url);
		return url;
	}

	/**
	 * Caches a map tile to file, unused
	 */
	private String cache(final String url, final int x, final int y, final int z) {

	 this.logger.debug(String.format("try to caching : x=%d, y=%d, z=%d", x, y, z));

		String mapDir = this.infra.getPath("map") + File.separator + this.name;
		if (!FileHelper.exists(mapDir)) {
			FileHelper.createDirs(mapDir);
		}
		if (!FileHelper.exists(mapDir)) {
			return url;
		}
		this.logger.debug("mapDir : " + mapDir);

		String cacheDir = mapDir + File.separator + z + File.separator + x;
		String cacheFile = cacheDir + File.separator + y + ".png";
		String cacheFileDownload = cacheFile + ".download";

		try {

			// if there is cached file
			if (FileHelper.exists(cacheFile)) {
//				this.logger.debug("cached : " + new File(cacheFile).toURI().toString());
				return new File(cacheFile).toURI().toString();
			}

			// if downloading...
			if (new File(cacheFileDownload).exists()) {
//				this.logger.debug("downloading now : " + url);
				return url;
			}

			// create path
			FileHelper.createDirs(cacheDir);

			// start downloading thread
			new CachingThread(url, cacheFile).start();

			// return original url
			return url;

		} catch (Exception ex) {
			ex.printStackTrace();
			return url;
		}
	}

	static class CachingThread extends Thread {

		String url;
		String localFile;

		public CachingThread(String url, String localFile) {
			this.url = url;
			this.localFile = localFile;
		}

		@Override
		public void run() {

			// temporary downloading file
			final String cacheFileDownload = this.localFile + ".download";

			try {

				URL u = new URL(url);
				URLConnection uc = u.openConnection();
				int contentLength = uc.getContentLength();
				InputStream raw = uc.getInputStream();
				InputStream in = new BufferedInputStream(raw);
				byte[] data = new byte[contentLength];
				int bytesRead = 0;
				int offset = 0;
				while (offset < contentLength) {
					bytesRead = in.read(data, offset, data.length - offset);
					if (bytesRead == -1) {
						break;
					}
					offset += bytesRead;
				}
				in.close();
				FileOutputStream out = new FileOutputStream(cacheFileDownload);
				out.write(data);
				out.flush();
				out.close();

//				TICASLogger.getLogger(this.getClass().getName()).debug("downloaded : " + localFile);
				new File(cacheFileDownload).renameTo(new File(localFile));

			} catch (Exception ex) {
			} finally {
				new File(cacheFileDownload).delete();
			}
		}
	}
}
