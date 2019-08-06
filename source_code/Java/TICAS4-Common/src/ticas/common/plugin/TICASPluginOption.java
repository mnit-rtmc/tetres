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

package ticas.common.plugin;

import javax.swing.JFrame;
import net.xeoh.plugins.base.options.AddPluginsFromOption;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public abstract class TICASPluginOption implements AddPluginsFromOption {

    public abstract void addTopMenu(javax.swing.JMenuItem menuItem);

    public abstract void addTabPanel(String tabLabel, javax.swing.JPanel panel);

    public abstract JFrame getMainWindow();
    
    public abstract void hideMainWindow();

    public abstract void showMainWindow();
    
}