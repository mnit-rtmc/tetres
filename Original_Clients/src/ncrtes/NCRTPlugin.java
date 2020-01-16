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


package ncrtes;

import net.xeoh.plugins.base.annotations.PluginImplementation;
import common.plugin.TICASPlugin;
import common.plugin.TICASPluginOption;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */

@PluginImplementation
public class NCRTPlugin implements TICASPlugin {

    @Override
    public void run(final TICASPluginOption ticasPluginOption) {
        NCRTESConfig.init();
        NCRTESPanel panMain = new NCRTESPanel(ticasPluginOption.getMainWindow());
        panMain.init();
        ticasPluginOption.addTabPanel("NCRTES Client", panMain);        
    }

    @Override
    public String getName() {
        return "Normal Condition Recovery Time Estimation System Client Plugin";
    }
    
}
