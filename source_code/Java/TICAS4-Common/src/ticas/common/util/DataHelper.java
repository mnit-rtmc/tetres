package ticas.common.util;

import ticas.common.config.Config;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.entity.mime.MultipartEntityBuilder;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.ByteArrayBody;
import net.lingala.zip4j.core.ZipFile;
import net.lingala.zip4j.model.ZipParameters;
import net.lingala.zip4j.util.Zip4jConstants;
import net.lingala.zip4j.exception.ZipException;
import java.io.*;

public class DataHelper {
	/**
	 * Uploads single byte array to server to be written as a file
	 */
	public static boolean uploadFile(ByteArrayOutputStream b, String name) {
		try (CloseableHttpClient client = HttpClientBuilder.create().build()) {
			HttpPost post = new HttpPost(Config.pythonServerURL + ":5000/tetres/uploadfile");
			post.setHeader("Accept", "application/json");
			MultipartEntityBuilder builder = MultipartEntityBuilder.create();
			builder.addPart("file", new ByteArrayBody(b.toByteArray(), name));
			post.setEntity(builder.build());
			HttpResponse response = client.execute(post);
			return response != null && String.valueOf(response.getStatusLine()
					.getStatusCode()).startsWith("2");
		} catch (IOException e) {
			e.printStackTrace();
		}
		return false;
	}

	/**
	 * Uploads entire config directory
	 */
	public static boolean uploadData() {
		HttpResponse response;
		try (CloseableHttpClient client = HttpClientBuilder.create().build()) {
			File data = new File(Config.getDataPath());
			File destFolder = new File(Config.getDataPath()).getParentFile();
			File dest = new File(destFolder.getAbsolutePath() + "/datafiles/data.zip");
			if (!dest.getParentFile().exists())
				dest.getParentFile().mkdirs();
			ZipFile zipFile = new ZipFile(dest);
			ZipParameters zipParams = new ZipParameters();
			zipParams.setCompressionMethod(Zip4jConstants.COMP_DEFLATE);
			zipParams.setCompressionLevel(Zip4jConstants.DEFLATE_LEVEL_NORMAL);
			zipFile.addFolder(data, zipParams);

			// Upload created zipFile
			HttpPost post = new HttpPost(Config.pythonServerURL + ":5000/tetres/uploaddata");
			post.setHeader("Accept", "application/json");
			MultipartEntityBuilder builder = MultipartEntityBuilder.create();
			builder.addPart("file", new FileBody(dest));
			post.setEntity(builder.build());
			response = client.execute(post);

		} catch (ZipException e) {
			e.printStackTrace();
			return false;
		} catch (IOException e) {
			e.printStackTrace();
			return false;
		}
		return response != null && String.valueOf(response.getStatusLine().getStatusCode()).startsWith("2");
	}

	/**
	 * Sends GET request to server to delete the file at deletePath
	 * deletePath should assume already in the server's data directory
	 */
	public static boolean deleteData(String deletePath) {
		HttpResponse response;
		try (CloseableHttpClient client = HttpClientBuilder.create().build()) {
			HttpGet get = new HttpGet(Config.pythonServerURL + ":5000/tetres/deletedata?path=" + deletePath);
			response = client.execute(get);
			System.out.println("\n\n\nResponse code: " + response + "\n\n\n");
		} catch (IOException e) {
			e.printStackTrace();
			return false;
		}
		return response != null && String.valueOf(response.getStatusLine().getStatusCode()).startsWith("2");
	}
}
