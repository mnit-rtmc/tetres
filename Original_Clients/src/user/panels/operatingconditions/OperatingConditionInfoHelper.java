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
package user.panels.operatingconditions;

import common.config.Config;
import common.infra.Infra;
import common.util.FileHelper;
import common.util.DataHelper;
import user.TeTRESConfig;
import user.filters.IFilterListChangeListener;
import user.types.OperatingConditionsInfo;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;

import java.io.ByteArrayOutputStream;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class OperatingConditionInfoHelper {

	private static List<IFilterListChangeListener> filterListChangeListeners = new ArrayList<IFilterListChangeListener>();

	private static List<OperatingConditionsInfo> ociList = new ArrayList<>();

	public static void addChangeListener(IFilterListChangeListener listener) {
		filterListChangeListeners.add(listener);
	}

	public static void removeChangeListener(IFilterListChangeListener listener) {
		filterListChangeListeners.remove(listener);
	}

	public  static List<OperatingConditionsInfo> loadOperatingConditionList() {
		for(IFilterListChangeListener listener : filterListChangeListeners)
			listener.filterGroupUpdated(ociList);
		return ociList;
	}

	public static void importOCs() {
		List<String> ocs = Config.getDownloadedOCs();
		for (String o : ocs)
			ociList.add(OperatingConditionsInfo.fromJSON(o));
	}

	static boolean exists(String name) {
		return name != null && ociList.stream().anyMatch(o -> name.equals(o.name));
	}

	static boolean save(OperatingConditionsInfo oci) {
		try {
			ociList.add(oci);
			byte[] bytes = oci.toJSON().getBytes("UTF-8");
			ByteArrayOutputStream baos = new ByteArrayOutputStream(bytes.length);
			baos.write(bytes, 0, bytes.length);
			return DataHelper.uploadFile(baos, "tetres/filters/" + oci.name + ".json");
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}

	// TODO: fix update button creating separate oci object in list
	static boolean update(OperatingConditionsInfo oci, String prevOCName) {
		boolean exists = exists(oci.name);
		boolean nameChanged = false;
		if (prevOCName != null) {
			if (!oci.name.equals(prevOCName)) {
				nameChanged = true;
			}
		}

		// Name changed to already existing name
		if(exists && nameChanged) {
			JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "The same operating condition name exists");
			return false;
		}

		boolean isSaved = save(oci);
		if (!isSaved) {
			return false;
		}

		if (nameChanged) {
			delete(prevOCName);
		}

		return true;
	}

	static boolean delete(OperatingConditionsInfo oci) {
		boolean removed = oci.name != null && ociList.removeIf(o -> oci.name.equals(o.name));
		String deletePath = "tetres/filters/" + oci.name + ".json";
		return removed && DataHelper.deleteData(deletePath);
	}

	static boolean delete(String name) {
		boolean removed = name != null && ociList.removeIf(o -> name.equals(o.name));
		String deletePath = "tetres/filters/" + name + ".json";
		return removed && DataHelper.deleteData(deletePath);
	}
}
