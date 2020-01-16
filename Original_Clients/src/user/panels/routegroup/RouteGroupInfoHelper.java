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
package user.panels.routegroup;

import common.config.Config;
import common.util.DataHelper;
import user.TeTRESConfig;
import user.types.RouteGroupInfo;

import java.io.ByteArrayOutputStream;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class RouteGroupInfoHelper {

	private static List<IRouteGroupListChangeListener> routeGroupListChangeListeners = new ArrayList<IRouteGroupListChangeListener>();

	public static List<RouteGroupInfo> routeGroups = new ArrayList<>();

	public static void addChangeListener(IRouteGroupListChangeListener listener) {
		routeGroupListChangeListeners.add(listener);
	}

	public static void removeChangeListener(IRouteGroupListChangeListener listener) {
		routeGroupListChangeListeners.remove(listener);
	}

	/**
	 * Adds route groups to GUI elements
	 */
	public static List<RouteGroupInfo> loadRouteGroups() {
		for (IRouteGroupListChangeListener listener : routeGroupListChangeListeners)
			listener.routeGroupUpdated(routeGroups);
		return routeGroups;
	}

	public static void importRouteGroups() {
		List<String> rGroups = Config.getDownloadedRouteGroups();
		for (String rg : rGroups) {
			System.out.println(rg);
			routeGroups.add(RouteGroupInfo.fromJSON(rg));
		}
	}

	static boolean exists(String name) {
		return name != null && routeGroups.stream().anyMatch(r -> name.equals(r.name));
	}

	static boolean save(RouteGroupInfo routeGroupInfo) {
		try {
			routeGroups.add(routeGroupInfo);
			byte[] bytes = routeGroupInfo.toJSON().getBytes("UTF-8");
			ByteArrayOutputStream baos = new ByteArrayOutputStream(bytes.length);
			baos.write(bytes, 0, bytes.length);
			return DataHelper.uploadFile(baos, "tetres/route-groups/" + routeGroupInfo.name + ".json");
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}

	static boolean update(RouteGroupInfo routeGroupInfo, String prevGroupName) {
		boolean exists = exists(routeGroupInfo.name);
		boolean nameChanged = false;
		if (prevGroupName != null) {
			if (!routeGroupInfo.name.equals(prevGroupName)) {
				nameChanged = true;
			}
		}

		// Name changed to already existing name
		if(exists && nameChanged) {
			JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "The same route group name exists");
			return false;
		}

		boolean isSaved = save(routeGroupInfo);
		if (!isSaved) {
			return false;
		}

		if (nameChanged) {
			delete(prevGroupName);
		}

		return true;
	}

	static boolean delete(RouteGroupInfo routeGroupInfo) {
		boolean removed = routeGroupInfo.name != null
			&& routeGroups.removeIf(r -> routeGroupInfo.name.equals(r.name));
		String deletePath = "tetres/route-groups/" + routeGroupInfo.name + ".json";
		return removed && DataHelper.deleteData(deletePath);
	}

	static boolean delete(String name) {
		boolean removed = name != null && routeGroups.removeIf(r -> name.equals(r.name));
		String deletePath = "tetres/route-groups/" + name + ".json";
		return removed && DataHelper.deleteData(deletePath);
	}
}
