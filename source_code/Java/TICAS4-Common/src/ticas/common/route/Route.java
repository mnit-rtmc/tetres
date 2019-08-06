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
package ticas.common.route;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.common.infra.Infra;
import ticas.common.infra.InfraConfig;
import ticas.common.infra.RNode;
import ticas.common.pyticas.types.RouteConfig;
import ticas.common.util.FileHelper;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;
import javax.xml.bind.DatatypeConverter;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Route {

    public String __module__;
    public String __class__;
    public String name;
    public String desc;
    public String infra_cfg_date;
    public RouteConfig cfg;
    private List<String> rnodes = new ArrayList<String>();
    private transient Infra infra = Infra.getInstance();

    public Route() {
        this("NoName", "NoDescription");
    }

    public Route(String name, String desc) {
        this.name = name;
        this.desc = desc;
        InfraConfig icfg = this.infra.getConfig();
        if (icfg != null) {
            this.__class__ = this.infra.getConfig().ROUTE_CLASS;
            this.__module__ = this.infra.getConfig().ROUTE_MODULE;
        }
    }

    public void addRNode(RNode rn) {
        this.rnodes.add(rn.name);
    }

    public void addRNode(String rnode_name) {
        this.rnodes.add(rnode_name);
    }

    public List<RNode> getRNodes() {
        List<RNode> rns = new ArrayList<RNode>();
        for (String rn_name : this.rnodes) {
            rns.add(this.infra.getRNode(rn_name));
        }
        return rns;
    }

    public List<String> getRNodeNames() {
        return this.rnodes;
    }

    public void save() throws IOException {
        String routeDir = infra.getPath("route");
        File routeCacheDir = new File(routeDir);
        if (!routeCacheDir.mkdir() && !routeCacheDir.exists()) {
            JOptionPane.showMessageDialog(null, "Fail to create cache folder\n" + routeCacheDir);
            return;
        }
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        String eName = getFileName(this.name);
        String filename = routeDir + File.separator + eName;
        FileHelper.writeTextFile(json, filename);
    }

    public static Route load(String filepath) throws IOException {
        if (!(new File(filepath).exists())) {
            return null;
        }
        Gson gson = new GsonBuilder().create();
        String jsonContent = FileHelper.readTextFile(filepath);
        Route s = gson.fromJson(jsonContent, Route.class);
        s.infra = Infra.getInstance();
        return s;
    }

    @Override
    public Route clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, Route.class);
    }

    public static String getFileName(String name) {
        return DatatypeConverter.printBase64Binary(name.getBytes());
        //return Base64.encode(name.getBytes());          
    }

    public static String getFilePath(String name) {
        String routeDir = Infra.getInstance().getPath("route");
        return routeDir + File.separator + getFileName(name);
    }

    public static List<String> getRouteFiles(boolean getNameOnly) {
        String routeDir = Infra.getInstance().getPath("route");
        System.err.println("routeDir:" + routeDir);
        return FileHelper.listFiles(routeDir, getNameOnly);
    }

    public static boolean saveRoute(Route r) {
        try {
            String filepath = getFilePath(r.name);

            Gson gsonBuilder = new GsonBuilder().create();
            String content = gsonBuilder.toJson(r);

            FileHelper.writeTextFile(content, filepath);
            return true;
        } catch (IOException ex) {
            Logger.getLogger(Route.class.getName()).log(Level.SEVERE, null, ex);
            return false;
        }
    }
    ////////////    

    @Override
    public String toString() {
        return this.name;
    }
}
